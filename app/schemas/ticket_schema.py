from app import ma
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from marshmallow import fields, validate, validates, ValidationError


VALID_STORY_POINTS = [1, 2, 3, 5, 8, 13]


class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True

    title = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200, error="title requis (2-200 caractères)")
    )
    owner_id = fields.Int(required=True)
    sprint_id = fields.Int(load_default=None)

    status = fields.Str(
        validate=validate.OneOf(
            [s.value for s in TicketStatus],
            error=f"status doit être parmi : {[s.value for s in TicketStatus]}"
        ),
        load_default=TicketStatus.TODO.value
    )
    priority = fields.Str(
        validate=validate.OneOf(
            [p.value for p in TicketPriority],
            error=f"priority doit être parmi : {[p.value for p in TicketPriority]}"
        ),
        load_default=TicketPriority.MEDIUM.value
    )
    ai_priority_hint = fields.Str(
        validate=validate.OneOf(
            ["urgent", "blocking", "normal"],
            error="ai_priority_hint doit être : urgent | blocking | normal"
        ),
        load_default=None
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("story_points")
    def validate_story_points(self, value):
        if value is not None and value not in VALID_STORY_POINTS:
            raise ValidationError(f"story_points doit être dans la suite Fibonacci : {VALID_STORY_POINTS}")


ticket_schema  = TicketSchema()
tickets_schema = TicketSchema(many=True)
