from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket_schema import ticket_schema, tickets_schema

bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")

VALID_STATUSES   = [s.value for s in TicketStatus]



@bp.route("", methods=["POST"])
def create_ticket():
    data = request.get_json()
    try:
        ticket = ticket_schema.load(data, session=db.session)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 201



@bp.route("", methods=["GET"])
def get_tickets():
    query = Ticket.query

    if status := request.args.get("status"):
        query = query.filter_by(status=status)
    if priority := request.args.get("priority"):
        query = query.filter_by(priority=priority)
    if sprint_id := request.args.get("sprint_id"):
        query = query.filter_by(sprint_id=sprint_id)
    if owner_id := request.args.get("owner_id"):
        query = query.filter_by(owner_id=owner_id)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return jsonify(tickets_schema.dump(tickets)), 200



@bp.route("/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    return jsonify(ticket_schema.dump(ticket)), 200



@bp.route("/<int:ticket_id>", methods=["PUT"])
def update_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    data = request.get_json()
    try:
        updated = ticket_schema.load(data, instance=ticket, partial=True, session=db.session)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    db.session.commit()
    return jsonify(ticket_schema.dump(updated)), 200


@bp.route("/<int:ticket_id>/status", methods=["PATCH"])
def update_status(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    data = request.get_json()
    new_status = data.get("status")

    if new_status not in VALID_STATUSES:
        return jsonify({"error": f"Statut invalide. Valeurs acceptées : {VALID_STATUSES}"}), 400

    ticket.status = new_status
    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200


# ─── PATCH — stocker le résultat IA (critères + story points + hint) ─────────
@bp.route("/<int:ticket_id>/ai", methods=["PATCH"])
def update_ai_fields(ticket_id):
    """
    Body attendu :
    {
        "acceptance_criteria": "- Critère 1\n- Critère 2",
        "story_points": 5,
        "ai_priority_hint": "urgent"
    }
    """
    ticket = db.get_or_404(Ticket, ticket_id)
    data = request.get_json()

    if "acceptance_criteria" in data:
        ticket.acceptance_criteria = data["acceptance_criteria"]
    if "story_points" in data:
        valid_fp = [1, 2, 3, 5, 8, 13]
        if data["story_points"] not in valid_fp:
            return jsonify({"error": f"story_points doit être dans {valid_fp}"}), 400
        ticket.story_points = data["story_points"]
    if "ai_priority_hint" in data:
        if data["ai_priority_hint"] not in ["urgent", "blocking", "normal"]:
            return jsonify({"error": "ai_priority_hint : urgent | blocking | normal"}), 400
        ticket.ai_priority_hint = data["ai_priority_hint"]

    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200



@bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_ticket(ticket_id):
    ticket = db.get_or_404(Ticket, ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} supprimé"}), 200
