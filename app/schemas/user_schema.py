from app import ma
from app.models.user import User
from marshmallow import fields, validate, pre_load, post_load


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password",)          # ne jamais exposer le hash en sortie

    username = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=80,
                                 error="username : 2 à 80 caractères")
    )
    email = fields.Email(
        required=True,
        error_messages={"invalid": "Email invalide"}
    )
    # En entrée seulement, jamais renvoyé en JSON
    password = fields.Str(
        load_only=True,
        required=True,
        validate=validate.Length(min=8,
                                 error="Mot de passe : 8 caractères minimum")
    )
    created_at = fields.DateTime(dump_only=True)

    # Retourne la liste des IDs (pas les objets complets → évite les boucles)
    assigned_tickets = fields.List(fields.Int(), dump_only=True)
    created_tickets  = fields.List(fields.Int(), dump_only=True)

    def get_attribute(self, obj, attr, default):
        if attr == "assigned_tickets":
            return [t.id for t in obj.assigned_tickets]
        if attr == "created_tickets":
            return [t.id for t in obj.created_tickets]
        return super().get_attribute(obj, attr, default)

    @post_load
    def hash_password(self, instance, **kwargs):
        """Hash automatique du mot de passe après chargement."""
        raw = self.context.get("_raw_password")
        if raw:
            instance.set_password(raw)
        return instance

    @pre_load
    def extract_password(self, data, **kwargs):
        """Extrait le password AVANT que marshmallow le valide,
        pour pouvoir le hasher dans post_load."""
        if "password" in data:
            self.context["_raw_password"] = data["password"]
        return data


user_schema  = UserSchema()
users_schema = UserSchema(many=True)