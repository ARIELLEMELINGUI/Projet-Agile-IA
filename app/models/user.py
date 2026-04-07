from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app.models.project_member import ProjectMember


class User(db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations

    #tickets = db.relationship("Ticket", backref="owner", lazy=True)
    project_members = db.relationship("ProjectMember",
                                      back_populates="user",
                                      lazy=True,
                                      cascade="all, delete-orphan")
    created_projects = db.relationship("Project",    back_populates="creator", lazy=True)
    created_tickets  = db.relationship("Ticket", foreign_keys="Ticket.created_by",
                                        back_populates="creator",  lazy=True)
    assigned_tickets = db.relationship("Ticket", foreign_keys="Ticket.assigned_to",
                                        back_populates="assignee", lazy=True)




    def set_password(self, raw: str):
        self.password = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password, raw)

    def membership_in(self, project_id: int):
        return ProjectMember.query.filter_by(
            user_id=self.id, project_id=project_id
        ).first()

    def role_in(self, project_id: int):
        """Retourne le rôle (str) dans un projet, ou None si non-membre."""
        m = self.membership_in(project_id)
        return m.role if m else None

    def __repr__(self):
        return f"<User {self.username}>"
