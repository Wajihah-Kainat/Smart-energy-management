# Subsystem 1: User and Building Management
# Pages: log in / register, buildings list (add + edit), building details (devices).
import re
from datetime import date
from functools import wraps

from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("s1", __name__)

BUILDING_TYPES = ("office", "university", "home")
ENERGY_TYPES = ("electricity", "gas", "solar")
DEFAULT_COMFORT_TEMP = 21.0
MIN_PASSWORD_LENGTH = 8
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------- login helpers
@bp.before_app_request
def load_logged_in_user():
    """Before every request: find out who is logged in (or nobody)."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    """Pages with this decorator can only be opened by a logged-in user."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("s1.login"))
        return view(*args, **kwargs)
    return wrapped_view


# ------------------------------------------------------------ validation helpers
def check_registration(name, email, password):
    """Return an error message, or None if everything is fine."""
    if not name:
        return "Please enter your name."
    if not EMAIL_PATTERN.match(email):
        return "Please enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"The password must have at least {MIN_PASSWORD_LENGTH} characters."
    return None


def check_building(name, address, building_type, comfort_text):
    """Return (error, comfort_temp). comfort_temp is a number when there is no error."""
    if not name:
        return "Please enter a building name.", None
    if not address:
        return "Please enter an address.", None
    if building_type not in BUILDING_TYPES:
        return "The type must be office, university or home.", None
    if comfort_text == "":
        return None, DEFAULT_COMFORT_TEMP          # empty -> default 21
    try:
        comfort_temp = float(comfort_text.replace(",", "."))
    except ValueError:
        return "The comfort temperature must be a number.", None
    if not 10 <= comfort_temp <= 30:
        return "The comfort temperature must be between 10 and 30 °C.", None
    return None, comfort_temp


def check_device(name, energy_type):
    if not name:
        return "Please enter a device name."
    if energy_type not in ENERGY_TYPES:
        return "The energy type must be electricity, gas or solar."
    return None


# ------------------------------------------------- ownership helpers (rule S1-N3)
def get_own_building(building_id):
    """Return the building if it belongs to the logged-in user, otherwise 404."""
    building = get_db().execute(
        "SELECT * FROM buildings WHERE id = ? AND user_id = ?",
        (building_id, g.user["id"])).fetchone()
    if building is None:
        abort(404)
    return building


def get_own_device(device_id):
    """Return the device if its building belongs to the logged-in user, otherwise 404."""
    device = get_db().execute(
        "SELECT d.* FROM devices d JOIN buildings b ON b.id = d.building_id "
        "WHERE d.id = ? AND b.user_id = ?", (device_id, g.user["id"])).fetchone()
    if device is None:
        abort(404)
    return device


# ------------------------------------------------------------ screen 1: log in
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Wrong email or password.", "error")
            return render_template("login.html", tab="login", form=request.form), 401
        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("s1.buildings"))
    return render_template("login.html", tab=request.args.get("tab", "login"), form={})


@bp.route("/register", methods=("POST",))
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    error = check_registration(name, email, password)
    db = get_db()
    if error is None and db.execute(
            "SELECT id FROM users WHERE email = ?", (email,)).fetchone():
        error = "This email address is already registered."      # requirement S1-F10
    if error:
        flash(error, "error")
        return render_template("login.html", tab="register", form=request.form), 400

    cursor = db.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, generate_password_hash(password), date.today().isoformat()))
    db.commit()
    session.clear()
    session["user_id"] = cursor.lastrowid                        # log in right away
    return redirect(url_for("s1.buildings"))


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("s1.login"))


# ------------------------------------------- screen 2: buildings list + add/edit
def show_buildings(form=None, edit_building=None, status=200):
    buildings = get_db().execute(
        "SELECT b.*, COUNT(d.id) AS device_count FROM buildings b "
        "LEFT JOIN devices d ON d.building_id = b.id "
        "WHERE b.user_id = ? GROUP BY b.id ORDER BY b.name", (g.user["id"],)).fetchall()
    return render_template("buildings.html", buildings=buildings, form=form or {},
                           edit_building=edit_building,
                           building_types=BUILDING_TYPES,
                           default_temp=int(DEFAULT_COMFORT_TEMP)), status


@bp.route("/buildings")
@login_required
def buildings():
    edit_building = None
    if request.args.get("edit"):
        edit_building = get_own_building(request.args.get("edit", type=int))
    return show_buildings(form=edit_building or {}, edit_building=edit_building)


@bp.route("/buildings/add", methods=("POST",))
@login_required
def add_building():
    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    building_type = request.form.get("type", "")
    error, comfort_temp = check_building(
        name, address, building_type, request.form.get("comfort_temp", "").strip())
    if error:
        flash(error, "error")
        return show_buildings(form=request.form, status=400)
    db = get_db()
    db.execute(
        "INSERT INTO buildings (user_id, name, address, type, comfort_temp) "
        "VALUES (?, ?, ?, ?, ?)", (g.user["id"], name, address, building_type, comfort_temp))
    db.commit()
    flash("Building saved.", "ok")
    return redirect(url_for("s1.buildings"))


@bp.route("/buildings/<int:building_id>/edit", methods=("POST",))
@login_required
def edit_building(building_id):
    building = get_own_building(building_id)
    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    building_type = request.form.get("type", "")
    error, comfort_temp = check_building(
        name, address, building_type, request.form.get("comfort_temp", "").strip())
    if error:
        flash(error, "error")
        return show_buildings(form=request.form, edit_building=building, status=400)
    db = get_db()
    db.execute(
        "UPDATE buildings SET name = ?, address = ?, type = ?, comfort_temp = ? WHERE id = ?",
        (name, address, building_type, comfort_temp, building_id))
    db.commit()
    flash("Building updated.", "ok")
    return redirect(url_for("s1.buildings"))


@bp.route("/buildings/<int:building_id>/delete", methods=("POST",))
@login_required
def delete_building(building_id):
    get_own_building(building_id)                 # 404 if it is not yours
    db = get_db()
    db.execute("DELETE FROM devices WHERE building_id = ?", (building_id,))
    db.execute("DELETE FROM buildings WHERE id = ?", (building_id,))
    db.commit()
    flash("Building deleted.", "ok")
    return redirect(url_for("s1.buildings"))


# -------------------------------------- screen 3: building details + devices
def show_building(building, form=None, edit_device=None, status=200):
    devices = get_db().execute(
        "SELECT * FROM devices WHERE building_id = ? ORDER BY name",
        (building["id"],)).fetchall()
    return render_template("building_detail.html", building=building, devices=devices,
                           form=form or {}, edit_device=edit_device,
                           energy_types=ENERGY_TYPES), status


@bp.route("/buildings/<int:building_id>")
@login_required
def building_detail(building_id):
    building = get_own_building(building_id)
    edit_device = None
    if request.args.get("edit_device"):
        edit_device = get_own_device(request.args.get("edit_device", type=int))
        if edit_device["building_id"] != building_id:
            abort(404)
    return show_building(building, form=edit_device or {}, edit_device=edit_device)


@bp.route("/buildings/<int:building_id>/devices", methods=("POST",))
@login_required
def add_device(building_id):
    building = get_own_building(building_id)
    name = request.form.get("name", "").strip()
    energy_type = request.form.get("energy_type", "")
    error = check_device(name, energy_type)
    if error:
        flash(error, "error")
        return show_building(building, form=request.form, status=400)
    db = get_db()
    db.execute("INSERT INTO devices (building_id, name, energy_type) VALUES (?, ?, ?)",
               (building_id, name, energy_type))
    db.commit()
    flash("Device added.", "ok")
    return redirect(url_for("s1.building_detail", building_id=building_id))


@bp.route("/devices/<int:device_id>/edit", methods=("POST",))
@login_required
def edit_device(device_id):
    device = get_own_device(device_id)
    building = get_own_building(device["building_id"])
    name = request.form.get("name", "").strip()
    energy_type = request.form.get("energy_type", "")
    error = check_device(name, energy_type)
    if error:
        flash(error, "error")
        return show_building(building, form=request.form, edit_device=device, status=400)
    db = get_db()
    db.execute("UPDATE devices SET name = ?, energy_type = ? WHERE id = ?",
               (name, energy_type, device_id))
    db.commit()
    flash("Device updated.", "ok")
    return redirect(url_for("s1.building_detail", building_id=building["id"]))


@bp.route("/devices/<int:device_id>/delete", methods=("POST",))
@login_required
def delete_device(device_id):
    device = get_own_device(device_id)
    building_id = device["building_id"]
    db = get_db()
    db.execute("DELETE FROM devices WHERE id = ?", (device_id,))
    db.commit()
    flash("Device deleted.", "ok")
    return redirect(url_for("s1.building_detail", building_id=building_id))
