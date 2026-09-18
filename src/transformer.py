from collections import defaultdict

from src.models import TimeEntry


def filter_by_month(entries: list[TimeEntry], mes: int, anio: int) -> list[TimeEntry]:
    """Filtra los registros correspondientes al mes y año indicados, omitiendo días feriados con 0 horas."""
    filtered = []
    for entry in entries:
        d = entry.fecha
        if d.month == mes and d.year == anio:
            # Omitir registros FERIADO con 0 horas según reglas de negocio
            if entry.horas == 0.0 and "feriado" in entry.notas.lower():
                continue
            filtered.append(entry)
    return filtered


def group_by_client(entries: list[TimeEntry]) -> dict[str, list[TimeEntry]]:
    """Agrupa los registros por cliente ordenando los clientes alfabéticamente

    y los registros internos por fecha de inicio, fecha de fin y tarea.
    """
    grouped = defaultdict(list)
    for entry in entries:
        grouped[entry.cliente].append(entry)

    # Ordenar clientes alfabéticamente
    sorted_clients = sorted(grouped.keys())
    result = {}
    for client in sorted_clients:
        client_entries = grouped[client]
        # Orden determinista: 1. fecha_inicio, 2. fecha_fin, 3. tarea
        client_entries.sort(key=lambda e: (e.fecha_inicio, e.fecha_fin, e.tarea))
        result[client] = client_entries

    return result


def calculate_client_summary(client_entries: list[TimeEntry]) -> dict:
    """Calcula métricas resumen por cliente (horas totales, cantidad de registros y días trabajados)."""
    horas_totales = sum(e.horas for e in client_entries)
    registros = len(client_entries)
    dias_trabajados = len({e.fecha for e in client_entries})
    return {
        "horas_totales": horas_totales,
        "registros": registros,
        "dias_trabajados": dias_trabajados,
    }


def calculate_general_summary(grouped_entries: dict[str, list[TimeEntry]]) -> dict:
    """Calcula el resumen general acumulado para todos los clientes."""
    total_horas = 0.0
    total_registros = 0
    clients_summary = {}

    for client, entries in grouped_entries.items():
        summary = calculate_client_summary(entries)
        clients_summary[client] = summary
        total_horas += summary["horas_totales"]
        total_registros += summary["registros"]

    return {
        "total_horas": total_horas,
        "total_registros": total_registros,
        "clients_summary": clients_summary,
    }
