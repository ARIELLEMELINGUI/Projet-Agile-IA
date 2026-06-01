from app import ma
from app.models.ticket import Ticket, TicketStatus, TicketPriority, FIBONACCI
from marshmallow import fields, validate, validates, ValidationError


class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True

    title = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200,
                                 error="title requis (2-200 caractères)")
    )
    # Champ correct : created_by (pas owner_id)
    created_by = fields.Int(required=True)
    project_id = fields.Int(required=True)
    sprint_id  = fields.Int(load_default=None, allow_none=True)
    assigned_to = fields.Int(load_default=None, allow_none=True)

    status = fields.Str(
        load_default=TicketStatus.TODO.value,
        validate=validate.OneOf(
            TicketStatus.ALL,
            error=f"status doit être parmi : {TicketStatus.ALL}"
        )
    )
    priority = fields.Str(
        load_default=TicketPriority.MEDIUM.value,
        validate=validate.OneOf(
            TicketPriority.ALL,
            error=f"priority doit être parmi : {TicketPriority.ALL}"
        )
    )
    ai_priority_hint = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(
            ["urgent", "blocking", "normal"],
            error="ai_priority_hint : urgent | blocking | normal"
        )
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nom de l'assigné en lecture seule (pratique pour l'affichage)
    assignee_username = fields.Method("get_assignee_username", dump_only=True)

    def get_assignee_username(self, obj):
        return obj.assignee.username if obj.assignee else None

    @validates("story_points")
    def validate_story_points(self, value):
        if value is not None and value not in FIBONACCI:
            raise ValidationError(
                f"story_points doit être dans la suite Fibonacci : {FIBONACCI}"
            )


ticket_schema  = TicketSchema()
tickets_schema = TicketSchema(many=True)