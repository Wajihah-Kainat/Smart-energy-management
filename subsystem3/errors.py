"""Single application-wide exception for subsystem validation and lookup errors."""


class AppError(Exception):
    """Unified exception used for input validation, lookup failures, and access issues."""

    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return self.message
