from flask import Blueprint, request, jsonify, session
from app import db
from app.models.ticket         import Ticket, TicketStatus, TicketPriority, FIBONACCI
from app.models.project_member import ProjectMember, Role
from app.models.user           import User

bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")


def _current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

def _get_pm(user_id, project_id):
    return ProjectMember.query.filter_by(user_id=user_id, project_id=project_id).first()

def _ticket_dict(t):
    return {
        "id":                  t.id,
        "title":               t.title,
        "description":         t.description,
        "status":              t.status,
        "priority":            t.priority,
        "story_points":        t.story_points,
        "acceptance_criteria": t.acceptance_criteria,
        "ai_priority_hint":    t.ai_priority_hint,
        "project_id":          t.project_id,
        "sprint_id":           t.sprint_id,
        "created_by":          t.created_by,
        "assigned_to":         t.assigned_to,
        "assignee_username":   t.assignee.username if t.assignee else None,
        "created_at":          t.created_at.isoformat(),
        "updated_at":          t.updated_at.isoformat(),
    }


# ─── CRÉER UN TICKET (PO ou SM) ──────────────────────────────────────────────
@bp.route("", methods=["POST"])
def create_ticket():
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401

    data       = request.get_json() or {}
    project_id = data.get("project_id")
    title      = data.get("title", "").strip()

    if not project_id or not title:
        return jsonify({"error": "project_id et title sont requis"}), 422

    pm = _get_pm(user.id, project_id)
    if not pm or pm.role == Role.DEVELOPER:
        return jsonify({"error": "Seul le PO ou SM peut créer des tickets"}), 403

    priority = data.get("priority", TicketPriority.MEDIUM)
    if priority not in TicketPriority.ALL:
        return jsonify({"error": f"priority doit être l'un de : {TicketPriority.ALL}"}), 422

    ticket = Ticket(
        title=title,
        description=data.get("description"),
        priority=priority,
        project_id=project_id,
        sprint_id=data.get("sprint_id"),      # None = backlog
        created_by=user.id,
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify(_ticket_dict(ticket)), 201


# ─── TOUS LES TICKETS D'UN PROJET ────────────────────────────────────────────
@bp.route("/project/<int:project_id>", methods=["GET"])
def get_tickets(project_id):
    """
    Tous les membres du projet voient tous les tickets.
    Filtre optionnel : ?sprint_id=3  ou  ?sprint_id=backlog
    """
    user = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401

    pm = _get_pm(user.id, project_id)
    if not pm:
        return jsonify({"error": "Vous n'êtes pas membre de ce projet"}), 403

    q = Ticket.query.filter_by(project_id=project_id)

    sprint_filter = request.args.get("sprint_id")
    if sprint_filter == "backlog":
        q = q.filter(Ticket.sprint_id.is_(None))
    elif sprint_filter:
        q = q.filter_by(sprint_id=int(sprint_filter))

    return jsonify([_ticket_dict(t) for t in q.order_by(Ticket.created_at.desc()).all()]), 200


# ─── ASSIGNER UN TICKET À UN MEMBRE ─────────────────────────────────────────
@bp.route("/<int:ticket_id>/assign", methods=["PATCH"])
def assign_ticket(ticket_id):
    """PO ou SM assigne un ticket à n'importe quel membre du projet."""
    user   = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    ticket = db.get_or_404(Ticket, ticket_id)

    pm = _get_pm(user.id, ticket.project_id)
    if not pm or pm.role == Role.DEVELOPER:
        return jsonify({"error": "Seul le PO ou SM peut assigner des tickets"}), 403

    data        = request.get_json() or {}
    assignee_id = data.get("assigned_to")

    # Vérifie que la cible est membre du projet
    if not _get_pm(assignee_id, ticket.project_id):
        return jsonify({"error": "Cet utilisateur n'est pas membre du projet"}), 422

    ticket.assigned_to = assignee_id
    db.session.commit()
    return jsonify(_ticket_dict(ticket)), 200


# ─── CHANGER LE STATUT (drag & drop Kanban) ──────────────────────────────────
@bp.route("/<int:ticket_id>/status", methods=["PATCH"])
def update_status(ticket_id):
    """
    Tous les membres peuvent changer le statut.
    RÈGLE : un Developer ne peut bouger QUE ses tickets assignés.
    PO et SM peuvent bouger n'importe quel ticket.
    """
    user   = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    ticket = db.get_or_404(Ticket, ticket_id)

    pm = _get_pm(user.id, ticket.project_id)
    if not pm:
        return jsonify({"error": "Vous n'êtes pas membre de ce projet"}), 403

    if pm.role == Role.DEVELOPER and ticket.assigned_to != user.id:
        return jsonify({"error": "Vous ne pouvez déplacer que vos propres tickets"}), 403

    new_status = (request.get_json() or {}).get("status")
    if new_status not in TicketStatus.ALL:
        return jsonify({"error": f"Statuts valides : {TicketStatus.ALL}"}), 400

    ticket.status = new_status
    db.session.commit()
    return jsonify(_ticket_dict(ticket)), 200


# ─── MODIFIER UN TICKET (PO ou SM) ───────────────────────────────────────────
@bp.route("/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    user   = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    ticket = db.get_or_404(Ticket, ticket_id)

    pm = _get_pm(user.id, ticket.project_id)
    if not pm or pm.role == Role.DEVELOPER:
        return jsonify({"error": "Seul le PO ou SM peut modifier un ticket"}), 403

    data = request.get_json() or {}
    if "title"       in data: ticket.title       = data["title"]
    if "description" in data: ticket.description = data["description"]
    if "priority"    in data:
        if data["priority"] not in TicketPriority.ALL:
            return jsonify({"error": f"priority doit être l'un de : {TicketPriority.ALL}"}), 422
        ticket.priority = data["priority"]
    if "sprint_id"   in data: ticket.sprint_id   = data["sprint_id"]
    if "story_points" in data:
        if data["story_points"] not in FIBONACCI:
            return jsonify({"error": f"story_points doit être dans {FIBONACCI}"}), 422
        ticket.story_points = data["story_points"]

    db.session.commit()
    return jsonify(_ticket_dict(ticket)), 200


# ─── SUPPRIMER UN TICKET (PO ou SM) ──────────────────────────────────────────
@bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    user   = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    ticket = db.get_or_404(Ticket, ticket_id)

    pm = _get_pm(user.id, ticket.project_id)
    if not pm or pm.role == Role.DEVELOPER:
        return jsonify({"error": "Seul le PO ou SM peut supprimer un ticket"}), 403

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} supprimé"}), 200


# ─── ANALYSE IA (PO ou SM) ───────────────────────────────────────────────────
@bp.route("/<int:ticket_id>/ai/analyze", methods=["POST"])
def ai_analyze(ticket_id):
    user   = _current_user()
    if not user:
        return jsonify({"error": "Connexion requise"}), 401
    ticket = db.get_or_404(Ticket, ticket_id)

    pm = _get_pm(user.id, ticket.project_id)
    if not pm or pm.role == Role.DEVELOPER:
        return jsonify({"error": "Seul le PO ou SM peut lancer l'analyse IA"}), 403

    try:
        from app.services.ai_service import analyze_ticket
        result = analyze_ticket(ticket.title, ticket.description or "")
    except Exception as e:
        return jsonify({"error": f"Erreur IA : {e}"}), 502

    ticket.acceptance_criteria = "\n".join(result.get("acceptance_criteria", []))
    ticket.story_points        = result.get("story_points")
    ticket.ai_priority_hint    = result.get("ai_priority_hint")
    db.session.commit()

    return jsonify({
        **_ticket_dict(ticket),
        "reasoning": result.get("reasoning"),
    }), 200