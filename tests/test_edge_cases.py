from datetime import datetime

import pytest

from src.exceptions import InvalidHeaderError
from src.models import TimeEntry
from src.parser import parse_csv_file
from src.transformer import filter_by_month
from src.validators import parse_duration


def test_edge_cases_problematic_data(tmp_path):
    """Prueba el parsing de datos problemáticos: decimales con coma (1,5) y notas con saltos de línea internos."""
    csv_content = (
        "Cliente;Usuario;Fecha de inicio;Fecha de fin;Duración;Horas;Proyecto;Tarea;Facturable;Facturado;Archivado;Zona horaria;Moneda;Notas\n"
        '"Cirion";"Rodrigo Gil";"03/08/2026 11:00:00";"03/08/2026 12:00:00";"1:30:00";"1,5";"Cirion";"Tarea 1";"true";"false";"false";"GMT-03:00";"USD";"Nota con salto\nde línea"\n'
    )
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content, encoding="utf-8-sig")

    entries = parse_csv_file(csv_file)
    assert len(entries) == 1
    assert entries[0].horas == 1.5
    assert "\n" in entries[0].notas


def test_parse_csv_english_headers_with_ampm(tmp_path):
    """Prueba el parsing de un CSV en inglés (headers en inglés) con formato de fecha AM/PM (12-hour)."""
    csv_content = (
        "Service;Client;Project;User;Task list;Task;Due date;Estimated hours;Billable;Billed;Hourly rate;Archived;Start date;End date;Timezone;Duration;Hours;Notes;Total;Hourly cost;Cost;Currency\n"
        '"";"CenturyLink";"CenturyLink";"Diego Salas";"";"CENT-1234 CDS Rediseño";"";"";"true";"false";"";"false";"07/01/2026 09:00:00 AM";"07/01/2026 01:00:00 PM";"GMT-03:00";"4:00:00";"4";"Mejoras estadísticas";"";"";"";"USD"\n'
    )
    csv_file = tmp_path / "test_english.csv"
    csv_file.write_text(csv_content, encoding="utf-8-sig")

    entries = parse_csv_file(csv_file)
    assert len(entries) == 1
    assert entries[0].cliente == "CenturyLink"
    assert entries[0].usuario == "Diego Salas"
    assert entries[0].horas == 4.0
    # Verificar que la fecha se parseó correctamente (9:00 AM = 09:00)
    assert entries[0].fecha_inicio.hour == 9
    assert entries[0].fecha_inicio.day == 1
    assert entries[0].fecha_inicio.month == 7
    assert entries[0].fecha_inicio.year == 2026


def test_parse_datetime_ampm_format():
    """Prueba que parse_datetime acepte formato 12-hour con AM/PM (ej. 07/01/2026 09:00:00 AM)."""
    from src.validators import parse_datetime

    # AM
    dt_am = parse_datetime("07/01/2026 09:00:00 AM", 1, "Start date")
    assert dt_am.hour == 9
    assert dt_am.day == 7
    assert dt_am.month == 1

    # PM
    dt_pm = parse_datetime("07/01/2026 01:00:00 PM", 1, "End date")
    assert dt_pm.hour == 13  # 1 PM = 13:00
    assert dt_pm.day == 7
    assert dt_pm.month == 1

    # 12 PM (noon)
    dt_noon = parse_datetime("07/01/2026 12:00:00 PM", 1, "Start date")
    assert dt_noon.hour == 12

    # 12 AM (midnight)
    dt_midnight = parse_datetime("07/01/2026 12:00:00 AM", 1, "Start date")
    assert dt_midnight.hour == 0


def test_parse_csv_english_headers_missing_required(tmp_path):
    """Prueba que un CSV en inglés sin columnas requeridas lance InvalidHeaderError."""
    csv_content = 'Service;Client;Project;User\n"CenturyLink";"Diego Salas"\n'
    csv_file = tmp_path / "bad_english.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    with pytest.raises(InvalidHeaderError):
        parse_csv_file(csv_file)


def test_filter_omits_feriados():
    """Prueba que filter_by_month omita registros marcados como FERIADO con 0 horas en las notas."""
    entry1 = TimeEntry(
        servicio=None,
        cliente="Cirion",
        proyecto="Cirion",
        usuario="Rodrigo Gil",
        lista_tareas=None,
        tarea="Trabajo",
        fecha_entrega=None,
        horas_estimadas=None,
        facturable=True,
        facturado=False,
        precio_hora=None,
        archivado=False,
        fecha_inicio=datetime(2026, 8, 10, 10, 0, 0),  # noqa: DTZ001
        fecha_fin=datetime(2026, 8, 10, 12, 0, 0),  # noqa: DTZ001
        zona_horaria="GMT-03:00",
        duracion_str="2:00:00",
        horas=2.0,
        notas="Normal",
        total=None,
        costo_hora=None,
        costo=None,
        moneda="USD",
    )
    entry_feriado = TimeEntry(
        servicio=None,
        cliente="Cirion",
        proyecto="Cirion",
        usuario="Rodrigo Gil",
        lista_tareas=None,
        tarea="Feriado",
        fecha_entrega=None,
        horas_estimadas=None,
        facturable=False,
        facturado=False,
        precio_hora=None,
        archivado=False,
        fecha_inicio=datetime(2026, 8, 17, 0, 0, 0),  # noqa: DTZ001
        fecha_fin=datetime(2026, 8, 17, 0, 0, 0),  # noqa: DTZ001
        zona_horaria="GMT-03:00",
        duracion_str="0:00:00",
        horas=0.0,
        notas="FERIADO",
        total=None,
        costo_hora=None,
        costo=None,
        moneda="USD",
    )

    filtered = filter_by_month([entry1, entry_feriado], 8, 2026)
    assert len(filtered) == 1
    assert filtered[0].tarea == "Trabajo"


def test_duration_over_24h():
    """Prueba que parse_duration acepte duraciones superiores a 24 horas (ej. 27:30:00)."""
    assert parse_duration("27:30:00", 1) == "27:30:00"


def test_missing_required_headers(tmp_path):
    """Prueba que se lance InvalidHeaderError cuando el CSV no contiene las columnas obligatorias."""
    csv_content = """Cliente;Usuario;Fecha de inicio
Cirion;Rodrigo Gil;03/08/2026 11:00:00
"""
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    with pytest.raises(InvalidHeaderError):
        parse_csv_file(csv_file)
