from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.user import User
from app.schemas.user_schema import user_schema, users_schema

bp = Blueprint("users", __name__, url_prefix="/api/users")


# ─── CREATE ───────────────────────────────────────────────────────────────────
@bp.route("", methods=["POST"])
def create_user():
    data = request.get_json()
    try:
        user = user_schema.load(data, session=db.session)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    # Unicité username / email
    if User.query.filter_by(username=user.username).first():
        return jsonify({"error": "username déjà utilisé"}), 409
    if User.query.filter_by(email=user.email).first():
        return jsonify({"error": "email déjà utilisé"}), 409

    db.session.add(user)
    db.session.commit()
    return jsonify(user_schema.dump(user)), 201


# ─── READ ALL ─────────────────────────────────────────────────────────────────
@bp.route("", methods=["GET"])
def get_users():
    role = request.args.get("role")
    query = User.query
    if role:
        query = query.filter_by(role=role)
    users = query.order_by(User.created_at.desc()).all()
    return jsonify(users_schema.dump(users)), 200


# ─── READ ONE ─────────────────────────────────────────────────────────────────
@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return jsonify(user_schema.dump(user)), 200


# ─── UPDATE ───────────────────────────────────────────────────────────────────
@bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.get_json()
    try:
        updated = user_schema.load(data, instance=user, partial=True, session=db.session)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    db.session.commit()
    return jsonify(user_schema.dump(updated)), 200


# ─── DELETE ───────────────────────────────────────────────────────────────────
@bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Utilisateur {user_id} supprimé"}), 200
