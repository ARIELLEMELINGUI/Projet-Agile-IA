from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User

bp = Blueprint("users", __name__, url_prefix="/api/users")


def _current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


def _user_dict(u):
    return {
        "id":         u.id,
        "username":   u.username,
        "email":      u.email,
        "created_at": u.created_at.isoformat(),
    }


# ─── LISTE TOUS LES USERS (utile pour chercher un membre à inviter) ───────────
@bp.route("", methods=["GET"])
def get_users():
    """
    GET /api/users          → tous les users
    GET /api/users?q=alice  → recherche par username ou email
    """
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401

    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(User.username.ilike(like), User.email.ilike(like))
        )
    users = query.order_by(User.username).all()
    return jsonify([_user_dict(u) for u in users]), 200


# ─── UN USER EN DÉTAIL ───────────────────────────────────────────────────────
@bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401

    target = db.get_or_404(User, user_id)
    return jsonify(_user_dict(target)), 200


# ─── MODIFIER SON PROPRE PROFIL ───────────────────────────────────────────────
@bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Un user ne peut modifier que son propre profil.
    Champs modifiables : username, email, password.
    """
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    if user.id != user_id:
        return jsonify({"error": "Vous ne pouvez modifier que votre propre profil"}), 403

    data = request.get_json() or {}

    if "username" in data:
        new_username = data["username"].strip()
        if len(new_username) < 2:
            return jsonify({"error": "username : 2 caractères minimum"}), 422
        # Vérifie unicité (sauf si c'est le sien)
        existing = User.query.filter_by(username=new_username).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "Username déjà utilisé"}), 409
        user.username = new_username

    if "email" in data:
        new_email = data["email"].strip().lower()
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "Email déjà utilisé"}), 409
        user.email = new_email

    if "password" in data:
        pwd = data["password"]
        if len(pwd) < 8:
            return jsonify({"error": "Mot de passe : 8 caractères minimum"}), 422
        user.set_password(pwd)

    db.session.commit()
    return jsonify(_user_dict(user)), 200


# ─── SUPPRIMER SON COMPTE ─────────────────────────────────────────────────────
@bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    if user.id != user_id:
        return jsonify({"error": "Vous ne pouvez supprimer que votre propre compte"}), 403

    db.session.delete(user)
    db.session.commit()
    session.clear()
    return jsonify({"message": "Compte supprimé"}), 200