import csv
from pathlib import Path

from src.exceptions import InvalidHeaderError
from src.models import TimeEntry
from src.validators import (
    parse_boolean,
    parse_datetime,
    parse_duration,
    parse_hours,
    validate_client,
    validate_headers,
    validate_single_user,
)


def parse_csv_file(file_path: Path, override_usuario: str | None = None) -> list[TimeEntry]:
    """Lee y procesa el archivo CSV de exportación de Tracking Time, convirtiéndolo en objetos TimeEntry."""
    entries = []
    users_found = set()

    # Abrir el archivo CSV con codificación utf-8-sig para manejar correctamente el BOM
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if not reader.fieldnames:
            raise InvalidHeaderError("El archivo CSV no contiene cabeceras.")

        # Validar que existan todas las cabeceras obligatorias requeridas
        validate_headers(list(reader.fieldnames))

        for idx, row in enumerate(reader, start=2):
            cliente = validate_client(row.get("Cliente") or "", idx)
            usuario_raw = row.get("Usuario")
            usuario = usuario_raw.strip() if usuario_raw else ""
            if not usuario and override_usuario:
                usuario = override_usuario
            if usuario:
                users_found.add(usuario)

            fecha_inicio = parse_datetime(row.get("Fecha de inicio") or "", idx, "Fecha de inicio")
            fecha_fin = parse_datetime(row.get("Fecha de fin") or "", idx, "Fecha de fin")
            duracion_str = parse_duration(row.get("Duración") or "", idx)
            horas = parse_hours(row.get("Horas") or "", idx)

            # Construir entidad de dominio con cada fila del CSV
            entry = TimeEntry(
                servicio=row.get("Servicio") or None,
                cliente=cliente,
                proyecto=row.get("Proyecto", "").strip(),
                usuario=usuario,
                lista_tareas=row.get("Lista de tareas") or None,
                tarea=row.get("Tarea", "").strip(),
                fecha_entrega=row.get("Fecha de entrega") or None,
                horas_estimadas=row.get("Horas estimadas") or None,
                facturable=parse_boolean(row.get("Facturable", "false")),
                facturado=parse_boolean(row.get("Facturado", "false")),
                precio_hora=row.get("Precio por hora") or None,
                archivado=parse_boolean(row.get("Archivado", "false")),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                zona_horaria=row.get("Zona horaria", "").strip(),
                duracion_str=duracion_str,
                horas=horas,
                notas=row.get("Notas", ""),
                total=row.get("Total") or None,
                costo_hora=row.get("Costo por hora") or None,
                costo=row.get("Costo") or None,
                moneda=row.get("Moneda", "USD").strip(),
            )
            entries.append(entry)

    # Validar que el archivo contenga registros de un único usuario
    if not override_usuario:
        validate_single_user(users_found)

    return entries
