from app import db
from datetime import datetime


class Sprint(db.Model):
    __tablename__ = "sprints"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    goal       = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date   = db.Column(db.Date)
    is_active  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    tickets = db.relationship("Ticket", backref="sprint", lazy=True)

    def __repr__(self):
        return f"<Sprint {self.name}>"
