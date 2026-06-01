from app import ma
from app.models.project import Project
from marshmallow import fields


class ProjectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True
        include_fk = True

    name        = fields.Str(required=True)
    description = fields.Str(load_default="", allow_none=True)
    created_by  = fields.Int(required=True)
    created_at  = fields.DateTime(dump_only=True)


    members = fields.List(
        fields.Nested("ProjectMemberSchema", only=("user_id", "role", "joined_at")),
        dump_only=True
    )


project_schema  = ProjectSchema()
projects_schema = ProjectSchema(many=True)