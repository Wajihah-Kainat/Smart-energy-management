
"""Manual CRUD test for ReadingManager."""

from services.reading_manager import ReadingManager

manager = ReadingManager("energy_test.db")

# Use an existing device from the test database.
readings = manager.list_all()
device_id = readings[0]["device_id"]

initial_count = len(readings)
print("Initial records:", initial_count)

# 1. Add a reading
new_id = manager.add(
    device_id=device_id,
    reading_date="2026-11-05",
    amount_kwh=5.5,
)
print("Added reading ID:", new_id)

assert len(manager.list_all()) == initial_count + 1

# 2. Update the new reading
manager.edit(
    reading_id=new_id,
    device_id=device_id,
    reading_date="2026-11-05",
    amount_kwh=8.5,
)

updated = next(
    r for r in manager.list_all()
    if r["id"] == new_id
)

assert updated["amount_kwh"] == 8.5
print("Update successful:", updated["amount_kwh"])

# 3. Delete the new reading
manager.delete(new_id)

assert len(manager.list_all()) == initial_count
print("Delete successful")

print("All CRUD tests passed!")
