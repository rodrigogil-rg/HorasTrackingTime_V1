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
    for req in REQUIRED_HEADERS:
        if req not in headers:
            raise InvalidHeaderError(f"El CSV no contiene la columna requerida: {req}")


def validate_month_year(mes: int, anio: int) -> None:
    if not isinstance(mes, int) or mes < 1 or mes > 12:
        raise InvalidMonthError(f"Mes inválido: {mes}. Debe estar entre 1 y 12.")
    if not isinstance(anio, int) or anio < 2000:
        raise InvalidYearError(f"Año inválido: {anio}. Debe ser >= 2000.")


def parse_boolean(val: str) -> bool:
    if not val:
        return False
    return val.strip().lower() in ("true", "1", "si", "yes")


def parse_hours(val: str, row_idx: int) -> float:
    if not val:
        raise InvalidHoursError(f"Fila {row_idx}: valor vacío en 'Horas'.")
    cleaned = val.strip().replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        raise InvalidHoursError(f"Fila {row_idx}: valor inválido en 'Horas': '{val}'")


def parse_datetime(val: str, row_idx: int, field_name: str) -> datetime:
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
        except ValueError:
            raise InvalidDateError(
                f"Fila {row_idx}: formato de fecha inválido en '{field_name}': '{val}'"
            )


def parse_duration(val: str, row_idx: int) -> str:
    if not val:
        raise InvalidDurationError(f"Fila {row_idx}: valor vacío en 'Duración'.")
    val_clean = val.strip()
    parts = val_clean.split(":")
    if len(parts) not in (2, 3):
        raise InvalidDurationError(f"Fila {row_idx}: formato de duración inválido: '{val}'")
    try:
        for p in parts:
            int(p)
    except ValueError:
        raise InvalidDurationError(f"Fila {row_idx}: formato de duración inválido: '{val}'")
    return val_clean


def validate_client(val: str, row_idx: int) -> str:
    if not val or not val.strip():
        raise EmptyClientError(f"Fila {row_idx}: el campo Cliente es obligatorio.")
    return val.strip()


def validate_single_user(users: set[str]) -> None:
    if len(users) > 1:
        raise MultipleUsersError(
            f"ERROR: Se detectaron múltiples usuarios en el CSV: {', '.join(sorted(users))}"
        )
