"""Try the Flask app of Subsystem 1 without starting a server.
Run it with the Run button in VS Code or:  python demo_app.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subsystem1.app import create_app

client = create_app().test_client()      # a fake browser that talks to our app


def show(title, response):
    print(f"{title}\n   status {response.status_code}: {response.get_json()}\n")


show("1. Register Arshia",
     client.post("/register", json={"name": "Arshia", "email": "arshia@example.com", "password": "secret123"}))
show("2. Register the same email again",
     client.post("/register", json={"name": "Arshia", "email": "ARSHIA@example.com", "password": "secret123"}))
show("3. Register with a bad email",
     client.post("/register", json={"name": "Bob", "email": "bob", "password": "secret123"}))
show("4. Register Bob",
     client.post("/register", json={"name": "Bob", "email": "bob@example.com", "password": "secret123"}))
show("5. Arshia adds a building",
     client.post("/buildings", json={"user_id": 1, "name": "Main Office", "address": "Hauptstrasse 1", "type": "office"}))
show("6. Add a building with a wrong type",
     client.post("/buildings", json={"user_id": 1, "name": "Castle", "address": "Hill 1", "type": "castle"}))
show("7. Arshia lists her buildings", client.get("/buildings?user_id=1"))
show("8. Bob tries to read Arshia's building", client.get("/buildings/1?user_id=2"))
show("9. Read a building that does not exist", client.get("/buildings/99?user_id=1"))
