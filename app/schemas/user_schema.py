from app import ma
from app.models.user import User
from marshmallow import fields, validate, ValidationError


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True

    # Validation rules
    username = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=80, error="username doit faire entre 2 et 80 caractères")
    )
    email = fields.Email(required=True, error_messages={"invalid": "Email invalide"})
    role = fields.Str(
        validate=validate.OneOf(
            ["developer", "product_owner", "scrum_master"],
            error="role doit être : developer | product_owner | scrum_master"
        )
    )
    created_at = fields.DateTime(dump_only=True)

    # Ne pas exposer les tickets imbriqués par défaut (évite les boucles)
    tickets = fields.List(fields.Int(), dump_only=True, attribute="ticket_ids")

    def get_attribute(self, obj, attr, default):
        if attr == "ticket_ids":
            return [t.id for t in obj.tickets]
        return super().get_attribute(obj, attr, default)


user_schema    = UserSchema()
users_schema   = UserSchema(many=True)
