
from app import ma
from app.models.sprint import Sprint, SprintStatus
from marshmallow import fields, validate


class SprintSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sprint
        load_instance = True
        include_fk = True

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120,
                                 error="name requis (max 120 caractères)")
    )
    goal       = fields.Str(load_default="", allow_none=True)
    start_date = fields.Date(format="%Y-%m-%d", load_default=None, allow_none=True)
    end_date   = fields.Date(format="%Y-%m-%d", load_default=None, allow_none=True)


    status = fields.Str(
        load_default=SprintStatus.PLANNING,
        validate=validate.OneOf(
            SprintStatus.ALL,
            error=f"status doit être parmi : {SprintStatus.ALL}"
        )
    )

    project_id = fields.Int(required=True)
    created_by = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

    ticket_ids = fields.List(fields.Int(), dump_only=True)

    def get_attribute(self, obj, attr, default):
        if attr == "ticket_ids":
            return [t.id for t in obj.tickets]
        return super().get_attribute(obj, attr, default)


sprint_schema  = SprintSchema()
sprints_schema = SprintSchema(many=True)
