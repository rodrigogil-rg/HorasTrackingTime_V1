from datetime import datetime

from src.exceptions import (
    EmptyClientError,
    InvalidDateError,
    InvalidDurationError,
    InvalidHeaderError,
    InvalidHoursError,
    InvalidMonthError,
    InvalidYearError,
    MultipleUsersError,
)

REQUIRED_HEADERS = [
    "Cliente",
    "Usuario",
    "Fecha de inicio",
    "Fecha de fin",
    "Duración",
    "Horas",
]

# Mapeo de encabezados en inglés a español para soportar archivos CSV exportados en inglés
HEADER_MAP_EN_ES = {
    "Service": "Servicio",
    "Client": "Cliente",
    "Project": "Proyecto",
    "User": "Usuario",
    "Task list": "Lista de tareas",
    "Task": "Tarea",
    "Due date": "Fecha de entrega",
    "Estimated hours": "Horas estimadas",
    "Billable": "Facturable",
    "Billed": "Facturado",
    "Hourly rate": "Precio por hora",
    "Archived": "Archivado",
    "Start date": "Fecha de inicio",
    "End date": "Fecha de fin",
    "Timezone": "Zona horaria",
    "Duration": "Duración",
    "Hours": "Horas",
    "Notes": "Notas",
    "Total": "Total",
    "Hourly cost": "Costo por hora",
    "Cost": "Costo",
    "Currency": "Moneda",
}


def normalize_headers(headers: list[str]) -> list[str]:
    """Normaliza encabezados traduciendo del inglés al español si es necesario."""
    normalized = []
    for h in headers:
        h_clean = h.strip()
        if h_clean in HEADER_MAP_EN_ES:
            normalized.append(HEADER_MAP_EN_ES[h_clean])
        else:
            normalized.append(h_clean)
    return normalized


def validate_headers(headers: list[str]) -> None:
    """Verifica que todas las columnas obligatorias estén presentes en el CSV."""
    normalized = normalize_headers(headers)
    for req in REQUIRED_HEADERS:
        if req not in normalized:
            raise InvalidHeaderError(f"El CSV no contiene la columna requerida: {req}")


def validate_month_year(mes: int, anio: int) -> None:
    """Valida que el mes esté entre 1 y 12 y el año sea mayor o igual a 2000."""
    if not isinstance(mes, int) or mes < 1 or mes > 12:
        raise InvalidMonthError(f"Mes inválido: {mes}. Debe estar entre 1 y 12.")
    if not isinstance(anio, int) or anio < 2000:
        raise InvalidYearError(f"Año inválido: {anio}. Debe ser >= 2000.")


def parse_boolean(val: str) -> bool:
    """Convierte un string booleano del CSV a valor booleano Python."""
    if not val:
        return False
    return val.strip().lower() in ("true", "1", "si", "yes")


def parse_hours(val: str, row_idx: int) -> float:
    """Parsea el campo de horas soportando comas decimales (ej. '1,5' -> 1.5)."""
    if not val:
        raise InvalidHoursError(f"Fila {row_idx}: valor vacío en 'Horas'.")
    cleaned = val.strip().replace(",", ".")
    try:
        return float(cleaned)
    except ValueError as exc:
        raise InvalidHoursError(f"Fila {row_idx}: valor inválido en 'Horas': '{val}'") from exc


def detect_date_format(date_str: str, is_english: bool = False) -> str:
    """Detecta si una fecha está en formato dd/mm/yyyy o mm/dd/yyyy.

    Reglas de detección:
    - Si el primer segmento > 12, es día (dd/mm/yyyy)
    - Si el segundo segmento > 12, es mes (mm/dd/yyyy)
    - Si ambos <= 12 (ambiguo):
      - Si is_english=True, asume mm/dd/yyyy (formato estadounidense)
      - Si is_english=False, asume dd/mm/yyyy (formato latinoamericano/europeo)

    Args:
        date_str: Cadena de fecha como "07/01/2026 09:00:00 AM" o "03/08/2026 11:00:00"
        is_english: Indica si los encabezados del CSV están en inglés

    Returns:
        Cadena de formato para strptime: "%d/%m/%Y" o "%m/%d/%Y"
    """
    if not date_str or not date_str.strip():
        return "%d/%m/%Y"

    # Extraer solo la parte de fecha (antes del espacio si hay hora)
    date_part = date_str.strip().split()[0]
    parts = date_part.split("/")

    if len(parts) != 3:
        return "%d/%m/%Y"

    try:
        first = int(parts[0])
        second = int(parts[1])
    except ValueError:
        return "%d/%m/%Y"

    # Si el primer segmento > 12, debe ser día (dd/mm/yyyy)
    if first > 12:
        return "%d/%m/%Y"

    # Si el segundo segmento > 12, debe ser mes (mm/dd/yyyy)
    if second > 12:
        return "%m/%d/%Y"

    # Ambos <= 12: ambiguo, usar contexto de idioma
    if is_english:
        return "%m/%d/%Y"

    return "%d/%m/%Y"


def parse_datetime(val: str, row_idx: int, field_name: str, is_english: bool = False) -> datetime:
    """Parsea cadenas de fecha/hora en formatos estándar y descarta información de zona horaria.
    Soporta formato 24-hour (HH:MM:SS) y 12-hour con AM/PM (hh:MM:SS AM/PM).
    Detecta automáticamente dd/mm/yyyy vs mm/dd/yyyy según el idioma del CSV."""
    if not val:
        raise InvalidDateError(f"Fila {row_idx}: valor vacío en '{field_name}'.")
    val_clean = val.strip()

    # Detectar formato de fecha basado en el primer registro
    date_format = detect_date_format(val_clean, is_english)

    # Intentar formatos de fecha/hora con el formato detectado primero
    formats = [
        f"{date_format} %H:%M:%S",  # 24-hour con formato detectado
        f"{date_format} %I:%M:%S %p",  # 12-hour con AM/PM y formato detectado
        "%d/%m/%Y %H:%M:%S",  # 24-hour fallback dd/mm/yyyy
        "%Y-%m-%d %H:%M:%S",  # ISO: 2026-08-03 11:00:00
        "%d/%m/%Y %I:%M:%S %p",  # 12-hour fallback dd/mm/yyyy
        "%m/%d/%Y %H:%M:%S",  # 24-hour fallback mm/dd/yyyy
        "%m/%d/%Y %I:%M:%S %p",  # 12-hour fallback mm/dd/yyyy
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(val_clean, fmt)  # noqa: DTZ007
            return dt.replace(tzinfo=None)
        except ValueError:
            continue
    raise InvalidDateError(f"Fila {row_idx}: formato de fecha inválido en '{field_name}': '{val}'")


def parse_duration(val: str, row_idx: int) -> str:
    """Valida y retorna la cadena de duración en formato H:MM:SS, o vacío si es feriado opcional."""
    if not val or not val.strip():
        return ""
    val_clean = val.strip()
    parts = val_clean.split(":")
    if len(parts) not in (2, 3):
        raise InvalidDurationError(f"Fila {row_idx}: formato de duración inválido: '{val}'")
    try:
        for p in parts:
            int(p)
    except ValueError as exc:
        raise InvalidDurationError(
            f"Fila {row_idx}: formato de duración inválido: '{val}'"
        ) from exc
    return val_clean


def validate_client(val: str, row_idx: int, is_feriado: bool = False) -> str:
    """Valida que el cliente no esté vacío, permitiendo omitirlo estrictamente si es un feriado."""
    if not val or not val.strip():
        if is_feriado:
            return "Feriado"
        raise EmptyClientError(f"Fila {row_idx}: el campo Cliente es obligatorio.")
    return val.strip()


def validate_single_user(users: set[str]) -> None:
    """Asegura que el reporte pertenezca a un único usuario."""
    if len(users) > 1:
        raise MultipleUsersError(
            f"ERROR: Se detectaron múltiples usuarios en el CSV: {', '.join(sorted(users))}"
        )
