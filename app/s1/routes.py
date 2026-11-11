# Subsystem 1: User and Building Management (pages)
# Pages: log in / register, buildings list (add + edit), building details (devices).
# The classes User, Building and Device are in models.py.
from functools import wraps

from flask import (Blueprint, abort, flash, g, redirect, render_template,
                   request, session, url_for)

from app.db import get_db
from .models import (BUILDING_TYPES, DEFAULT_COMFORT_TEMP, ENERGY_TYPES,
                     Building, Device, User)

bp = Blueprint("s1", __name__)


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
        user = User.find_by_email(get_db(), email)
        if user is None or not user.password_matches(password):
            flash("Wrong email or password.", "error")
            return render_template("login.html", tab="login", form=request.form), 401
        session.clear()
        session["user_id"] = user.id
        return redirect(url_for("s1.buildings"))
    return render_template("login.html", tab=request.args.get("tab", "login"), form={})


@bp.route("/register", methods=("POST",))
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    error = User.check_registration(name, email, password)
    db = get_db()
    if error is None and User.find_by_email(db, email):
        error = "This email address is already registered."      # requirement S1-F10
    if error:
        flash(error, "error")
        return render_template("login.html", tab="register", form=request.form), 400

    user = User.create(name, email, password)
    user.insert(db)
    session.clear()
    session["user_id"] = user.id                                 # log in right away
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
    error, comfort_temp = Building.check(
        name, address, building_type, request.form.get("comfort_temp", "").strip())
    if error:
        flash(error, "error")
        return show_buildings(form=request.form, status=400)
    Building(g.user["id"], name, address, building_type, comfort_temp).insert(get_db())
    flash("Building saved.", "ok")
    return redirect(url_for("s1.buildings"))


@bp.route("/buildings/<int:building_id>/edit", methods=("POST",))
@login_required
def edit_building(building_id):
    building = get_own_building(building_id)
    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    building_type = request.form.get("type", "")
    error, comfort_temp = Building.check(
        name, address, building_type, request.form.get("comfort_temp", "").strip())
    if error:
        flash(error, "error")
        return show_buildings(form=request.form, edit_building=building, status=400)
    Building(g.user["id"], name, address, building_type, comfort_temp,
             id=building_id).update(get_db())
    flash("Building updated.", "ok")
    return redirect(url_for("s1.buildings"))


@bp.route("/buildings/<int:building_id>/delete", methods=("POST",))
@login_required
def delete_building(building_id):
    get_own_building(building_id)                 # 404 if it is not yours
    Building.delete(get_db(), building_id)
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
    error = Device.check(name, energy_type)
    if error:
        flash(error, "error")
        return show_building(building, form=request.form, status=400)
    Device(building_id, name, energy_type).insert(get_db())
    flash("Device added.", "ok")
    return redirect(url_for("s1.building_detail", building_id=building_id))


@bp.route("/devices/<int:device_id>/edit", methods=("POST",))
@login_required
def edit_device(device_id):
    device = get_own_device(device_id)
    building = get_own_building(device["building_id"])
    name = request.form.get("name", "").strip()
    energy_type = request.form.get("energy_type", "")
    error = Device.check(name, energy_type)
    if error:
        flash(error, "error")
        return show_building(building, form=request.form, edit_device=device, status=400)
    Device(building["id"], name, energy_type, id=device_id).update(get_db())
    flash("Device updated.", "ok")
    return redirect(url_for("s1.building_detail", building_id=building["id"]))


@bp.route("/devices/<int:device_id>/delete", methods=("POST",))
@login_required
def delete_device(device_id):
    device = get_own_device(device_id)
    building_id = device["building_id"]
    Device.delete(get_db(), device_id)
    flash("Device deleted.", "ok")
    return redirect(url_for("s1.building_detail", building_id=building_id))
