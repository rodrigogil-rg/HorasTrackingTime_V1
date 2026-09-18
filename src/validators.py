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


def validate_headers(headers: list[str]) -> None:
    """Verifica que todas las columnas obligatorias estén presentes en el CSV."""
    for req in REQUIRED_HEADERS:
        if req not in headers:
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


def parse_datetime(val: str, row_idx: int, field_name: str) -> datetime:
    """Parsea cadenas de fecha/hora en formatos estándar y descarta información de zona horaria."""
    if not val:
        raise InvalidDateError(f"Fila {row_idx}: valor vacío en '{field_name}'.")
    val_clean = val.strip()
    try:
        dt = datetime.strptime(val_clean, "%d/%m/%Y %H:%M:%S")  # noqa: DTZ007
        return dt.replace(tzinfo=None)
    except ValueError:
        try:
            dt = datetime.strptime(val_clean, "%Y-%m-%d %H:%M:%S")  # noqa: DTZ007
            return dt.replace(tzinfo=None)
        except ValueError as exc:
            raise InvalidDateError(
                f"Fila {row_idx}: formato de fecha inválido en '{field_name}': '{val}'"
            ) from exc


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
