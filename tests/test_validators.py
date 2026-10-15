import pytest

from src.exceptions import (
    EmptyClientError,
    InvalidDateError,
    InvalidHoursError,
    MultipleUsersError,
)
from src.validators import (
    parse_datetime,
    parse_hours,
    validate_client,
    validate_single_user,
)


def test_parse_hours_valid():
    """Prueba el parsing de horas con formato de coma decimal: '1,5' -> 1.5, '2' -> 2.0, ' 3,25 ' -> 3.25."""
    assert parse_hours("1,5", 1) == 1.5
    assert parse_hours("2", 1) == 2.0
    assert parse_hours(" 3,25 ", 1) == 3.25


def test_parse_hours_invalid():
    """Prueba que parse_hours lance InvalidHoursError para valores no numéricos ('abc') o vacíos."""
    with pytest.raises(InvalidHoursError):
        parse_hours("abc", 1)
    with pytest.raises(InvalidHoursError):
        parse_hours("", 1)


def test_parse_datetime_valid():
    """Prueba el parsing de fechas en formato DD/MM/YYYY HH:MM:SS."""
    dt = parse_datetime("03/08/2026 11:00:00", 1, "Fecha de inicio")
    assert dt.year == 2026
    assert dt.month == 8
    assert dt.day == 3
    assert dt.hour == 11


def test_parse_datetime_invalid():
    """Prueba que parse_datetime lance InvalidDateError para formato de fecha inválido."""
    with pytest.raises(InvalidDateError):
        parse_datetime("invalid-date", 1, "Fecha de inicio")


def test_validate_client():
    """Prueba la validación del cliente: nombre válido aceptado, cadena vacía y solo espacios lanzan EmptyClientError."""
    assert validate_client("Cirion", 1) == "Cirion"
    with pytest.raises(EmptyClientError):
        validate_client("", 1)
    with pytest.raises(EmptyClientError):
        validate_client("   ", 1)


def test_validate_single_user():
    """Prueba que validate_single_user acepte un único usuario y lance MultipleUsersError para varios usuarios."""
    validate_single_user({"Rodrigo Gil"})
    with pytest.raises(MultipleUsersError):
        validate_single_user({"Rodrigo Gil", "Juan Perez"})
