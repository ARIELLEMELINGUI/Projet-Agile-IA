from flask import Blueprint, request, jsonify, session
from app import db
from app.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "username, email et password sont requis"}), 422
    if len(password) < 8:
        return jsonify({"error": "Mot de passe : 8 caractères minimum"}), 422
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email déjà utilisé"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username déjà utilisé"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify(_user_dict(user)), 201


@bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    session["user_id"] = user.id
    return jsonify(_user_dict(user)), 200


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Déconnecté"}), 200


@bp.route("/me", methods=["GET"])
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "Non authentifié"}), 401

    user = db.get_or_404(User, uid)

    # project_members est le bon nom de la relation (pas memberships)
    projects = []
    for m in user.project_members:
        projects.append({
            "id":          m.project.id,
            "name":        m.project.name,
            "description": m.project.description,
            "my_role":     m.role,
            "created_by":  m.project.created_by,
        })

    assigned = []
    for t in user.assigned_tickets:
        assigned.append({
            "id":           t.id,
            "title":        t.title,
            "status":       t.status,
            "priority":     t.priority,
            "story_points": t.story_points,
            "project_id":   t.project_id,
            "project_name": t.project.name,
            "sprint_id":    t.sprint_id,
        })

    return jsonify({
        "user":             _user_dict(user),
        "projects":         projects,
        "assigned_tickets": assigned,
    }), 200


def _user_dict(user):
    return {
        "id":         user.id,
        "username":   user.username,
        "email":      user.email,
        "created_at": user.created_at.isoformat(),
    }