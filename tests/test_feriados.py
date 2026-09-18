from datetime import datetime

from src.models import TimeEntry
from src.transformer import filter_by_month


def test_filter_omits_feriados():
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
