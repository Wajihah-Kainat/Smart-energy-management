from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash

from subsystem1 import User, Building
from subsystem1.error_handler import (
    Subsystem1ErrorHandler,
    DuplicateEmailError,
    AccessDeniedError,
    NotFoundError,
)


def create_app():
    """Build a small Flask app for Subsystem 1 (data is kept in memory for now)."""
    app = Flask(__name__)
    handler = Subsystem1ErrorHandler()
    users = {}        # user_id -> User
    buildings = {}    # building_id -> Building
    counter = {"user": 0, "building": 0}

    def error_response(error):
        """Turn an error into a JSON message and the right HTTP status code."""
        message = handler.handle(error)
        if isinstance(error, DuplicateEmailError):
            code = 409
        elif isinstance(error, AccessDeniedError):
            code = 403
        elif isinstance(error, NotFoundError):
            code = 404
        elif isinstance(error, (ValueError, TypeError)):
            code = 400
        else:
            code = 500
        return jsonify({"error": message}), code

    def building_to_dict(building):
        return {
            "id": building.get_id(),
            "user_id": building.get_user_id(),
            "name": building.get_name(),
            "address": building.get_address(),
            "type": building.get_type(),
            "comfort_temp": building.get_comfort_temp(),
        }

    def find_user(user_id):
        if user_id not in users:
            raise NotFoundError("This user does not exist.")
        return users[user_id]

    @app.route("/register", methods=["POST"])
    def register():
        try:
            data = request.get_json(silent=True) or {}
            email = data.get("email") or ""
            password = data.get("password")
            if not password:
                raise ValueError("Password must not be empty.")
            handler.check_unique_email([u.get_email() for u in users.values()], email)
            user = User(counter["user"] + 1, data.get("name"), email, generate_password_hash(password))
        except Exception as error:
            return error_response(error)
        counter["user"] += 1         # count only after the user was created successfully
        users[user.get_id()] = user
        return jsonify({"id": user.get_id(), "name": user.get_name(), "email": user.get_email()}), 201

    @app.route("/buildings", methods=["POST"])
    def add_building():
        try:
            data = request.get_json(silent=True) or {}
            find_user(data.get("user_id"))
            building = Building(counter["building"] + 1, data.get("user_id"), data.get("name"),
                                data.get("address"), data.get("type"), data.get("comfort_temp"))
        except Exception as error:
            return error_response(error)
        counter["building"] += 1
        buildings[building.get_id()] = building
        return jsonify(building_to_dict(building)), 201

    @app.route("/buildings", methods=["GET"])
    def list_buildings():
        try:
            user_id = request.args.get("user_id", type=int)
            find_user(user_id)
        except Exception as error:
            return error_response(error)
        own = [building_to_dict(b) for b in buildings.values() if b.get_user_id() == user_id]
        return jsonify(own), 200

    @app.route("/buildings/<int:building_id>", methods=["GET"])
    def get_building(building_id):
        try:
            user_id = request.args.get("user_id", type=int)
            find_user(user_id)
            if building_id not in buildings:
                raise NotFoundError("This building does not exist.")
            building = buildings[building_id]
            handler.check_owner(user_id, building)
        except Exception as error:
            return error_response(error)
        return jsonify(building_to_dict(building)), 200

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
