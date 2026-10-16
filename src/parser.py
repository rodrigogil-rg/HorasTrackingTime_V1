import csv
from pathlib import Path

from src.exceptions import InvalidHeaderError
from src.models import TimeEntry
from src.validators import (
    normalize_headers,
    parse_boolean,
    parse_datetime,
    parse_duration,
    parse_hours,
    validate_client,
    validate_headers,
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

        # Normalizar encabezados (traducir del inglés al español si es necesario)
        normalized_headers = normalize_headers(list(reader.fieldnames))

        # Validar que existan todas las cabeceras obligatorias requeridas (después de normalizar)
        validate_headers(normalized_headers)

        # Construir mapeo de nombre original -> nombre normalizado para traducir filas
        header_mapping = {}
        for orig, norm in zip(reader.fieldnames, normalized_headers):
            header_mapping[orig] = norm

        for idx, row in enumerate(reader, start=2):
            # Traducir la fila usando el mapeo de encabezados para acceder por nombre en español
            row_es = {}
            for orig_key, val in row.items():
                norm_key = header_mapping.get(orig_key, orig_key)
                row_es[norm_key] = val

            notas_val = row_es.get("Notas", "")
            horas_val = row_es.get("Horas", "")

            # Detectar si es un registro de feriado (notas contiene FERIADO u horas son 0 y sin cliente)
            is_feriado = "feriado" in notas_val.lower() or (
                not row_es.get("Cliente") and not horas_val.strip()
            )

            cliente = validate_client(row_es.get("Cliente") or "", idx, is_feriado=is_feriado)
            usuario_raw = row_es.get("Usuario")
            usuario = usuario_raw.strip() if usuario_raw else ""
            if not usuario and override_usuario:
                usuario = override_usuario
            if usuario:
                users_found.add(usuario)

            fecha_inicio = parse_datetime(
                row_es.get("Fecha de inicio") or "", idx, "Fecha de inicio"
            )
            fecha_fin = parse_datetime(row_es.get("Fecha de fin") or "", idx, "Fecha de fin")

            duracion_val = row_es.get("Duración") or ""
            if is_feriado and not duracion_val.strip():
                duracion_str = "0:00:00"
            else:
                duracion_str = parse_duration(duracion_val, idx)

            horas = (
                parse_hours(horas_val or "0", idx)
                if (is_feriado and not horas_val.strip())
                else parse_hours(horas_val, idx)
            )

            # Construir entidad de dominio con cada fila del CSV
            entry = TimeEntry(
                servicio=row_es.get("Servicio") or None,
                cliente=cliente,
                proyecto=row_es.get("Proyecto", "").strip(),
                usuario=usuario,
                lista_tareas=row_es.get("Lista de tareas") or None,
                tarea=row_es.get("Tarea", "").strip() or ("Feriado" if is_feriado else ""),
                fecha_entrega=row_es.get("Fecha de entrega") or None,
                horas_estimadas=row_es.get("Horas estimadas") or None,
                facturable=parse_boolean(row_es.get("Facturable", "false")),
                facturado=parse_boolean(row_es.get("Facturado", "false")),
                precio_hora=row_es.get("Precio por hora") or None,
                archivado=parse_boolean(row_es.get("Archivado", "false")),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                zona_horaria=row_es.get("Zona horaria", "").strip(),
                duracion_str=duracion_str,
                horas=horas,
                notas=notas_val,
                total=row_es.get("Total") or None,
                costo_hora=row_es.get("Costo por hora") or None,
                costo=row_es.get("Costo") or None,
                moneda=row_es.get("Moneda", "USD").strip(),
            )
            entries.append(entry)

    # Nota: Se permiten múltiples usuarios en el reporte consolidado
    return entries
