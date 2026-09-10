class TrackingTimeError(Exception):
    code: str = "UNKNOWN_ERROR"
    exit_code: int = 1


class InputNotFoundError(TrackingTimeError):
    code = "INPUT_NOT_FOUND"
    exit_code = 2


class MultipleInputFilesError(TrackingTimeError):
    code = "MULTIPLE_INPUT_FILES"
    exit_code = 2


class InvalidMonthError(TrackingTimeError):
    code = "INVALID_MONTH"
    exit_code = 2


class InvalidYearError(TrackingTimeError):
    code = "INVALID_YEAR"
    exit_code = 2


class InvalidHeaderError(TrackingTimeError):
    code = "INVALID_HEADER"
    exit_code = 1


class InvalidRowError(TrackingTimeError):
    code = "INVALID_ROW"
    exit_code = 1


class InvalidDateError(TrackingTimeError):
    code = "INVALID_DATE"
    exit_code = 1


class InvalidHoursError(TrackingTimeError):
    code = "INVALID_HOURS"
    exit_code = 1


class InvalidDurationError(TrackingTimeError):
    code = "INVALID_DURATION"
    exit_code = 1


class EmptyClientError(TrackingTimeError):
    code = "EMPTY_CLIENT"
    exit_code = 1


class MultipleUsersError(TrackingTimeError):
    code = "MULTIPLE_USERS"
    exit_code = 1


class OutputError(TrackingTimeError):
    code = "OUTPUT_ERROR"
    exit_code = 1
