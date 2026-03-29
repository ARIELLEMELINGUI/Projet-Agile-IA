from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80), unique=False, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    role       = db.Column(db.String(30), default="developer")  # developer | product_owner | scrum_master
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    tickets = db.relationship("Ticket", backref="owner", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
