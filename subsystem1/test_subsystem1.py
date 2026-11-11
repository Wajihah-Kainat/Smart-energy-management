import pytest
from subsystem1 import User, Building, Device


def test_user_constructor_and_getters():
    user = User(1, "  Hammad ", "Hammad@Example.com", "hash")
    assert user.get_name() == "Hammad"
    assert user.get_email() == "hammad@example.com"
    assert user.get_created_at() != ""


def test_user_rejects_bad_email():
    with pytest.raises(ValueError):
        User(1, "Hammad", "no-at-sign", "hash")


def test_user_update_profile():
    user = User(1, "Hammad", "a@b.com", "hash")
    user.update_profile("Ali", "ali@b.com")
    assert user.get_name() == "Ali"


def test_building_default_comfort_temp():
    building = Building(1, 1, "Home", "Street 1", "home")
    assert building.get_comfort_temp() == 21.0


def test_building_rejects_bad_type_and_temp():
    with pytest.raises(ValueError):
        Building(1, 1, "Home", "Street 1", "castle")
    building = Building(1, 1, "Home", "Street 1", "home")
    with pytest.raises(ValueError):
        building.set_comfort_temp(50)


def test_building_edit():
    building = Building(1, 1, "Home", "Street 1", "home")
    building.edit("Uni", "Campus 2", "university", 20)
    assert building.get_type() == "university"
    assert building.get_comfort_temp() == 20


def test_device_and_building_link():
    building = Building(1, 1, "Home", "Street 1", "home")
    device = Device(1, 1, "Heating", "Gas")
    building.add_device(device)
    assert building.get_devices() == [device]
    assert device.get_energy_type() == "gas"


def test_device_from_other_building_is_rejected():
    building = Building(1, 1, "Home", "Street 1", "home")
    with pytest.raises(ValueError):
        building.add_device(Device(1, 99, "Heating", "Gas"))
