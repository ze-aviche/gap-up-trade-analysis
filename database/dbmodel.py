# models.py
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
#from app import db

db = SQLAlchemy()

class GapUpResult(db.Model):
    __tablename__ = 'gap_up_result'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(16), index=True)
    result_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #To create tables (run once in a Python shell):
        
    #db.create_all()

    def __repr__(self):
        return f"<GapUpResult {self.ticker} at {self.created_at.isoformat()}>"