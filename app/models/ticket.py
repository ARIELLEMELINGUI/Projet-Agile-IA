from app import db
from datetime import datetime
import enum


class TicketStatus(str, enum.Enum):
    TODO        = "To Do"
    IN_PROGRESS = "In Progress"
    DONE        = "Done"


class TicketPriority(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    BLOCKING = "blocking"


class Ticket(db.Model):
    __tablename__ = "tickets"

    id                  = db.Column(db.Integer, primary_key=True)
    title               = db.Column(db.String(200), nullable=False)
    description         = db.Column(db.Text)
    status              = db.Column(db.String(20), default=TicketStatus.TODO.value)
    priority            = db.Column(db.String(20), default=TicketPriority.MEDIUM.value)
    story_points        = db.Column(db.Integer)
    acceptance_criteria = db.Column(db.Text)
    ai_priority_hint    = db.Column(db.String(50))
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at          = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    owner_id  = db.Column(db.Integer, db.ForeignKey("users.id"),   nullable=False)
    sprint_id = db.Column(db.Integer, db.ForeignKey("sprints.id"), nullable=True)

    def __repr__(self):
        return f"<Ticket {self.id} – {self.title}>"
