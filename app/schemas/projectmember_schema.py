from app import ma
from app.models.project_member import ProjectMember, Role
from marshmallow import fields, validate


class ProjectMemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProjectMember
        load_instance = True
        include_fk = True

    user_id    = fields.Int(required=True)
    project_id = fields.Int(required=True)
    role = fields.Str(
        required=True,
        validate=validate.OneOf(
            Role.ALL,
            error=f"role doit être parmi : {Role.ALL}"
        )
    )
    joined_at = fields.DateTime(dump_only=True)

    # Infos user en lecture seule (utile pour lister les membres)
    user = fields.Nested(
        "UserSchema",
        only=("id", "username", "email"),
        dump_only=True
    )


projectmember_schema  = ProjectMemberSchema()
projectmembers_schema = ProjectMemberSchema(many=True)