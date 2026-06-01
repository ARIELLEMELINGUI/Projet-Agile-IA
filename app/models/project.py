from datetime import datetime
from app import db

class Project(db.Model):
    __tablename__ = "projects"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_by  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    creator = db.relationship("User", back_populates="created_projects")
    members = db.relationship("ProjectMember", back_populates="project", lazy=True,
                                      cascade="all, delete-orphan")

    sprints = db.relationship("Sprint", back_populates="project", lazy=True)
    tickets = db.relationship("Ticket", back_populates="project", lazy=True)

    def __repr__(self):
        return f"<Project {self.name}>"