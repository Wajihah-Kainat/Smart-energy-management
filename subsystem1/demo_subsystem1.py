"""Small demo of Subsystem 1. Run it with the Run button in VS Code or:  python demo_subsystem1.py"""
import os
import sys
 
# Let Python find the folder "subsystem1" even when this file is run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from subsystem1 import User, Building, Device
 
user = User(1, "Arshia", "Arshia@Example.com", "demo_hash_123")
print(user)
 
building = Building(1, user.get_id(), "Main Office", "Hauptstrasse 1", "office")
print(building)                              # comfort temp = default 21.0
 
building.set_comfort_temp(22.5)              # setter
print("New comfort temp:", building.get_comfort_temp())
 
heater = Device(1, building.get_id(), "Heating", "Gas")
building.add_device(heater)
print(heater)
print("Devices in building:", [str(d) for d in building.get_devices()])
 
try:
    building.set_type("castle")              # wrong value -> error
except ValueError as error:
    print("Error caught:", error)
 
