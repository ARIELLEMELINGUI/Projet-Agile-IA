from app import db
from datetime import datetime


class SprintStatus:
    PLANNING = "planning"
    ACTIVE   = "active"
    DONE     = "done"
    ALL      = [PLANNING, ACTIVE, DONE]

class Sprint(db.Model):
    __tablename__ = "sprints"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    goal       = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date   = db.Column(db.Date)
    status     = db.Column(db.String(20), default=SprintStatus.PLANNING)
    #is_active  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relations
    project = db.relationship("Project", back_populates="sprints")
    creator = db.relationship("User",    foreign_keys=[created_by])
    tickets = db.relationship("Ticket", back_populates="sprint", lazy=True)

    def activate(self):
        """Un seul sprint actif à la fois par projet."""
        Sprint.query.filter_by(
            project_id=self.project_id,
            status=SprintStatus.ACTIVE
        ).update({"status": SprintStatus.DONE})
        self.status = SprintStatus.ACTIVE


    def close(self):
        """Clôt le sprint. Les tickets non-Done repassent au backlog."""
        self.status = SprintStatus.DONE
        for t in self.tickets:
            if t.status != "Done":
                t.sprint_id = None

    def __repr__(self):
        return f"<Sprint {self.name}>"
