class TrackingTimeError(Exception):
    """Excepción base para todos los errores de dominio de la aplicación."""

    code: str = "UNKNOWN_ERROR"
    exit_code: int = 1


class InputNotFoundError(TrackingTimeError):
    """Se lanza cuando no se encuentra el directorio o archivo CSV de entrada."""

    code = "INPUT_NOT_FOUND"
    exit_code = 2


class MultipleInputFilesError(TrackingTimeError):
    """Se lanza cuando se encuentran múltiples archivos CSV en el directorio de entrada."""

    code = "MULTIPLE_INPUT_FILES"
    exit_code = 2


class InvalidMonthError(TrackingTimeError):
    """Se lanza cuando el mes especificado no es válido (fuera del rango 1-12)."""

    code = "INVALID_MONTH"
    exit_code = 2


class InvalidYearError(TrackingTimeError):
    """Se lanza cuando el año especificado es inválido (< 2000)."""

    code = "INVALID_YEAR"
    exit_code = 2


class InvalidHeaderError(TrackingTimeError):
    """Se lanza cuando faltan columnas obligatorias en el archivo CSV."""

    code = "INVALID_HEADER"
    exit_code = 1


class InvalidRowError(TrackingTimeError):
    """Se lanza cuando una fila del CSV contiene datos corruptos o inválidos."""

    code = "INVALID_ROW"
    exit_code = 1


class InvalidDateError(TrackingTimeError):
    """Se lanza cuando el formato de fecha/hora en el CSV no es parseable."""

    code = "INVALID_DATE"
    exit_code = 1


class InvalidHoursError(TrackingTimeError):
    """Se lanza cuando el campo de horas no se puede convertir a número decimal."""

    code = "INVALID_HOURS"
    exit_code = 1


class InvalidDurationError(TrackingTimeError):
    """Se lanza cuando el formato de duración es incorrecto."""

    code = "INVALID_DURATION"
    exit_code = 1


class EmptyClientError(TrackingTimeError):
    """Se lanza cuando el campo de cliente está vacío u omitido."""

    code = "EMPTY_CLIENT"
    exit_code = 1


class MultipleUsersError(TrackingTimeError):
    """Se lanza cuando se detectan múltiples usuarios distintos en el CSV."""

    code = "MULTIPLE_USERS"
    exit_code = 1


class OutputError(TrackingTimeError):
    """Se lanza cuando ocurre un error al generar o guardar el archivo Excel."""

    code = "OUTPUT_ERROR"
    exit_code = 1
