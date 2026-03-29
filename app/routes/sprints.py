from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app import db
from app.models.sprint import Sprint
from app.schemas.sprint_schema import sprint_schema, sprints_schema

bp = Blueprint("sprints", __name__, url_prefix="/api/sprints")



@bp.route("", methods=["POST"])
def create_sprint():
    data = request.get_json()
    try:
        sprint = sprint_schema.load(data, session=db.session)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    # Un seul sprint actif à la fois
    if sprint.is_active:
        Sprint.query.filter_by(is_active=True).update({"is_active": False})

    db.session.add(sprint)
    db.session.commit()
    return jsonify(sprint_schema.dump(sprint)), 201



@bp.route("", methods=["GET"])
def get_sprints():
    active_only = request.args.get("active")
    query = Sprint.query
    if active_only == "true":
        query = query.filter_by(is_active=True)
    sprints = query.order_by(Sprint.created_at.desc()).all()
    return jsonify(sprints_schema.dump(sprints)), 200



@bp.route("/<int:sprint_id>", methods=["GET"])
def get_sprint(sprint_id):
    sprint = db.get_or_404(Sprint, sprint_id)
    return jsonify(sprint_schema.dump(sprint)), 200



@bp.route("/<int:sprint_id>", methods=["PUT"])
def update_sprint(sprint_id):
    sprint = db.get_or_404(Sprint, sprint_id)
    data = request.get_json()
    try:
        updated = sprint_schema.load(data, instance=sprint, partial=True, session=db.session)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if updated.is_active:
        Sprint.query.filter(Sprint.id != sprint_id, Sprint.is_active == True).update({"is_active": False})

    db.session.commit()
    return jsonify(sprint_schema.dump(updated)), 200



@bp.route("/<int:sprint_id>", methods=["DELETE"])
def delete_sprint(sprint_id):
    sprint = db.get_or_404(Sprint, sprint_id)
    db.session.delete(sprint)
    db.session.commit()
    return jsonify({"message": f"Sprint {sprint_id} supprimé"}), 200



@bp.route("/<int:sprint_id>/tickets", methods=["GET"])
def get_sprint_tickets(sprint_id):
    from app.schemas.ticket_schema import tickets_schema as ts
    sprint = db.get_or_404(Sprint, sprint_id)
    return jsonify(ts.dump(sprint.tickets)), 200
