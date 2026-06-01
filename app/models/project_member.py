from datetime import datetime
from app import db

class Role:
    PRODUCT_OWNER = "product_owner"
    SCRUM_MASTER  = "scrum_master"
    DEVELOPER     = "developer"
    ALL           = [PRODUCT_OWNER, SCRUM_MASTER, DEVELOPER]

class ProjectMember(db.Model):
    __tablename__ = "project_members"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    role       = db.Column(db.String(30), nullable=False)
    joined_at  = db.Column(db.DateTime, default=datetime.utcnow)

    user    = db.relationship("User",    back_populates="project_members")
    project = db.relationship("Project", back_populates="members")



    __table_args__ = (
        db.UniqueConstraint("user_id", "project_id", name="uq_one_role_per_project"),
    )

    def __repr__(self):
        return f"<ProjectMember user={self.user_id} project={self.project_id} role={self.role}>"