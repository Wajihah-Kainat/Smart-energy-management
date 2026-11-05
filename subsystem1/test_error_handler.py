import pytest
from subsystem1 import User, Building, Device
from subsystem1.error_handler import (
    Subsystem1ErrorHandler,
    DuplicateEmailError,
    AccessDeniedError,
    Subsystem1Error,
)


@pytest.fixture
def handler():
    return Subsystem1ErrorHandler()


def test_handle_value_error(handler):
    message = handler.handle(ValueError("Name must not be empty."))
    assert message == "Invalid input: Name must not be empty."


def test_handle_type_error(handler):
    message = handler.handle(TypeError("bad type"))
    assert message.startswith("Wrong type of value")


def test_handle_unexpected_error(handler):
    message = handler.handle(RuntimeError("something broke"))
    assert message.startswith("Unexpected error")


def test_run_safely_success(handler):
    result, error = handler.run_safely(User, 1, "Arshia", "a@b.com", "hash")
    assert error is None
    assert result.get_name() == "Arshia"


def test_run_safely_catches_bad_email(handler):
    result, error = handler.run_safely(User, 1, "Arshia", "no-at-sign", "hash")
    assert result is None
    assert "Invalid input" in error


def test_run_safely_catches_type_error(handler):
    building = Building(1, 1, "Home", "Street 1", "home")
    result, error = handler.run_safely(building.set_comfort_temp, "hot")
    assert result is None
    assert "Wrong type of value" in error


def test_run_safely_catches_bad_building_type(handler):
    result, error = handler.run_safely(Building, 1, 1, "Home", "Street 1", "castle")
    assert result is None
    assert "office" in error


def test_errors_are_logged_and_cleared(handler):
    handler.handle(ValueError("one"))
    handler.handle(ValueError("two"))
    assert handler.get_error_count() == 2
    handler.clear_errors()
    assert handler.get_errors() == []


def test_duplicate_email_is_blocked(handler):
    with pytest.raises(DuplicateEmailError):
        handler.check_unique_email(["a@b.com"], "A@B.com")


def test_new_email_is_allowed(handler):
    handler.check_unique_email(["a@b.com"], "other@b.com")   # no error expected


def test_other_users_building_is_denied(handler):
    building = Building(1, 1, "Home", "Street 1", "home")
    with pytest.raises(AccessDeniedError):
        handler.check_owner(2, building)


def test_owner_may_use_own_building(handler):
    building = Building(1, 1, "Home", "Street 1", "home")
    handler.check_owner(1, building)                         # no error expected


def test_duplicate_email_is_a_subsystem1_error(handler):
    message = handler.handle(DuplicateEmailError("x"))
    assert message.startswith("Email problem")
    assert issubclass(DuplicateEmailError, Subsystem1Error)


def test_device_with_empty_name_is_caught(handler):
    result, error = handler.run_safely(Device, 1, 1, "  ", "gas")
    assert result is None
    assert "Device name" in error


def test_not_found_error_message(handler):
    from subsystem1.error_handler import NotFoundError
    assert handler.handle(NotFoundError("x")).startswith("Not found")
