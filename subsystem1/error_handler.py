class Subsystem1Error(Exception):
    """Base class for all errors that are special to Subsystem 1."""


class DuplicateEmailError(Subsystem1Error):
    """Raised when someone registers with an email that already exists (requirement F10)."""


class AccessDeniedError(Subsystem1Error):
    """Raised when a user tries to use data of another user (requirement N3)."""


class NotFoundError(Subsystem1Error):
    """Raised when a user or building does not exist."""


class Subsystem1ErrorHandler:
    """Catches errors of Subsystem 1 and turns them into clear messages (requirement N4)."""

    def __init__(self):
        self._errors = []   # a log of all error messages

    # ---------- getters ----------
    def get_errors(self):
        return list(self._errors)

    def get_error_count(self):
        return len(self._errors)

    # ---------- main methods ----------
    def handle(self, error):
        """Turn one error into a clear message, save it in the log and return it."""
        if isinstance(error, DuplicateEmailError):
            message = f"Email problem: {error}"
        elif isinstance(error, AccessDeniedError):
            message = f"Access denied: {error}"
        elif isinstance(error, NotFoundError):
            message = f"Not found: {error}"
        elif isinstance(error, ValueError):
            message = f"Invalid input: {error}"
        elif isinstance(error, TypeError):
            message = f"Wrong type of value: {error}"
        else:
            message = f"Unexpected error: {error}"
        self._errors.append(message)
        return message

    def run_safely(self, function, *args, **kwargs):
        """Run a function. Returns (result, None) if it works, or (None, message) if it fails."""
        try:
            return function(*args, **kwargs), None
        except Exception as error:      # try / except from the Python tutorial
            return None, self.handle(error)

    def clear_errors(self):
        self._errors = []

    # ---------- checks that raise our own errors ----------
    def check_unique_email(self, existing_emails, email):
        """Raise DuplicateEmailError if the email is already used."""
        used = [e.strip().lower() for e in existing_emails]
        if email.strip().lower() in used:
            raise DuplicateEmailError(f"The email {email} is already registered.")

    def check_owner(self, user_id, building):
        """Raise AccessDeniedError if the building belongs to another user."""
        if building.get_user_id() != user_id:
            raise AccessDeniedError("This building belongs to another user.")
