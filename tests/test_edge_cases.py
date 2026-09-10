import pytest

from src.exceptions import InvalidHeaderError
from src.parser import parse_csv_file
from src.validators import parse_duration


def test_edge_cases_problematic_data(tmp_path):
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


def test_duration_over_24h():
    assert parse_duration("27:30:00", 1) == "27:30:00"


def test_missing_required_headers(tmp_path):
    csv_content = """Cliente;Usuario;Fecha de inicio
Cirion;Rodrigo Gil;03/08/2026 11:00:00
"""
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    with pytest.raises(InvalidHeaderError):
        parse_csv_file(csv_file)
