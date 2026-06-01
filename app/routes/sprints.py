from flask import Blueprint, request, jsonify, session
from app import db
from app.models.sprint import Sprint
from app.models.user import User

bp = Blueprint("sprints", __name__, url_prefix="/api/sprints")


def _current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


def _sprint_dict(s):
    return {
        "id":         s.id,
        "name":       s.name,
        "goal":       s.goal,
        "status":     s.status,
        "start_date": s.start_date.isoformat() if s.start_date else None,
        "end_date":   s.end_date.isoformat()   if s.end_date   else None,
        "project_id": s.project_id,
        "created_by": s.created_by,
        "created_at": s.created_at.isoformat(),
    }


@bp.route("", methods=["POST"])
def create_sprint():
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401

    data = request.get_json() or {}
    name       = data.get("name", "").strip()
    project_id = data.get("project_id")
    created_by = data.get("created_by", user.id)

    if not name or not project_id:
        return jsonify({"error": "name et project_id sont requis"}), 422

    from datetime import date
    start = None
    end   = None
    if data.get("start_date"):
        try: start = date.fromisoformat(data["start_date"])
        except: pass
    if data.get("end_date"):
        try: end = date.fromisoformat(data["end_date"])
        except: pass

    sprint = Sprint(
        name=name,
        goal=data.get("goal", ""),
        start_date=start,
        end_date=end,
        project_id=project_id,
        created_by=user.id,
    )
    db.session.add(sprint)
    db.session.commit()
    return jsonify(_sprint_dict(sprint)), 201


@bp.route("", methods=["GET"])
def get_sprints():
    project_id = request.args.get("project_id")
    query = Sprint.query
    if project_id:
        query = query.filter_by(project_id=int(project_id))
    sprints = query.order_by(Sprint.created_at.desc()).all()
    return jsonify([_sprint_dict(s) for s in sprints]), 200


@bp.route("/<int:sprint_id>", methods=["GET"])
def get_sprint(sprint_id):
    sprint = db.get_or_404(Sprint, sprint_id)
    return jsonify(_sprint_dict(sprint)), 200


@bp.route("/<int:sprint_id>", methods=["DELETE"])
def delete_sprint(sprint_id):
    sprint = db.get_or_404(Sprint, sprint_id)
    db.session.delete(sprint)
    db.session.commit()
    return jsonify({"message": f"Sprint {sprint_id} supprimé"}), 200


@bp.route("/<int:sprint_id>/tickets", methods=["GET"])
def get_sprint_tickets(sprint_id):
    sprint = db.get_or_404(Sprint, sprint_id)
    from app.routes.tickets import _ticket_dict
    return jsonify([_ticket_dict(t) for t in sprint.tickets]), 200