from flask import Blueprint, request, jsonify, session
from app import db
from app.models.project    import Project
from app.models.project_member import ProjectMember, Role
from app.models.user       import User

bp = Blueprint("projects", __name__, url_prefix="/api/projects")


def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

def require_login():
    u = current_user()
    if not u:
        return None, (jsonify({"error": "Connexion requise"}), 401)
    return u, None

def get_membership(user_id, project_id):
    return ProjectMember.query.filter_by(user_id=user_id, project_id=project_id).first()


# ─── CRÉER UN PROJET ─────────────────────────────────────────────────────────
@bp.route("", methods=["POST"])
def create_project():
    """
    N'importe quel user connecté peut créer un projet.
    Il choisit son propre rôle dans ce projet au moment de la création.
    """
    user, err = require_login()
    if err: return err

    data = request.get_json() or {}
    name = data.get("name", "").strip()
    role = data.get("my_role", Role.PRODUCT_OWNER)   # rôle du créateur

    if not name:
        return jsonify({"error": "name est requis"}), 422
    if role not in Role.ALL:
        return jsonify({"error": f"my_role doit être : {Role.ALL}"}), 422

    # 1. Crée le projet
    project = Project(
        name=name,
        description=data.get("description", ""),
        created_by=user.id
    )
    db.session.add(project)
    db.session.flush()   # génère project.id sans commit

    # 2. Ajoute le créateur comme membre avec son rôle choisi
    membership = ProjectMember(user_id=user.id, project_id=project.id, role=role)
    db.session.add(membership)
    db.session.commit()

    return jsonify({
        "id":          project.id,
        "name":        project.name,
        "description": project.description,
        "created_by":  project.created_by,
        "my_role":     role,
    }), 201


# ─── MES PROJETS ─────────────────────────────────────────────────────────────
@bp.route("", methods=["GET"])
def get_my_projects():
    user, err = require_login()
    if err: return err

    result = []
    for m in user.project_members:
        result.append({
            "id":          m.project.id,
            "name":        m.project.name,
            "description": m.project.description,
            "my_role":     m.role,
            "created_by":  m.project.created_by,
            "created_at":  m.project.created_at.isoformat(),
        })
    return jsonify(result), 200


# ─── UN PROJET EN DÉTAIL ─────────────────────────────────────────────────────
@bp.route("/<int:project_id>", methods=["GET"])
def get_project(project_id):
    user, err = require_login()
    if err: return err

    m = get_membership(user.id, project_id)
    if not m:
        return jsonify({"error": "Vous n'êtes pas membre de ce projet"}), 403

    project = db.get_or_404(Project, project_id)
    members = [{
        "user_id":  mb.user_id,
        "username": mb.user.username,
        "role":     mb.role,
    } for mb in project.members]

    return jsonify({
        "id":          project.id,
        "name":        project.name,
        "description": project.description,
        "my_role":     m.role,
        "members":     members,
        "created_at":  project.created_at.isoformat(),
    }), 200


# ─── AJOUTER UN MEMBRE ────────────────────────────────────────────────────────
@bp.route("/<int:project_id>/members", methods=["POST"])
def add_member(project_id):
    """
    Seul un PO ou SM du projet peut inviter quelqu'un.
    L'invité doit avoir un compte (on l'identifie par email).
    On lui attribue un rôle au moment de l'invitation.
    """
    user, err = require_login()
    if err: return err

    caller_m = get_membership(user.id, project_id)
    if not caller_m or caller_m.role not in (Role.PRODUCT_OWNER, Role.SCRUM_MASTER):
        return jsonify({"error": "Seul le PO ou SM peut inviter des membres"}), 403

    data  = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    role  = data.get("role", "")

    if not email or not role:
        return jsonify({"error": "email et role sont requis"}), 422
    if role not in Role.ALL:
        return jsonify({"error": f"role doit être : {Role.ALL}"}), 422

    # Cherche l'utilisateur par email
    target = User.query.filter_by(email=email).first()
    if not target:
        return jsonify({"error": f"Aucun compte trouvé pour {email}"}), 404

    # Vérifie qu'il n'est pas déjà membre
    if get_membership(target.id, project_id):
        return jsonify({"error": f"{target.username} est déjà membre du projet"}), 409

    new_membership = ProjectMember(user_id=target.id, project_id=project_id, role=role)
    db.session.add(new_membership)
    db.session.commit()

    return jsonify({
        "message":  f"{target.username} ajouté en tant que {role}",
        "user_id":  target.id,
        "username": target.username,
        "role":     role,
    }), 201


# ─── RETIRER UN MEMBRE ────────────────────────────────────────────────────────
@bp.route("/<int:project_id>/members/<int:target_user_id>", methods=["DELETE"])
def remove_member(project_id, target_user_id):
    user, err = require_login()
    if err: return err

    caller_m = get_membership(user.id, project_id)
    if not caller_m or caller_m.role not in (Role.PRODUCT_OWNER, Role.SCRUM_MASTER):
        return jsonify({"error": "Seul le PO ou SM peut retirer des membres"}), 403

    target_m = get_membership(target_user_id, project_id)
    if not target_m:
        return jsonify({"error": "Cet utilisateur n'est pas membre"}), 404

    db.session.delete(target_m)
    db.session.commit()
    return jsonify({"message": "Membre retiré"}), 200