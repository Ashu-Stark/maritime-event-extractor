
"""
Database models for SoF Event Extractor
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid


db = SQLAlchemy()


class Document(db.Model):
    """Document model for storing uploaded files"""
    __tablename__ = 'documents'
    
    id = db.Column(
        db.String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, unique=True)
    status = db.Column(db.String(20), default='uploaded')
    text_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Relationship
    events = db.relationship(
        'Event', 
        backref='document', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'status': self.status,
            'created_at': (
                self.created_at.isoformat() if self.created_at else None
            ),
            'processed_at': (
                self.processed_at.isoformat() if self.processed_at else None
            )
        }


class Event(db.Model):
    """Event model for storing extracted events"""
    __tablename__ = 'events'
    
    id = db.Column(
        db.String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    document_id = db.Column(
        db.String(36), 
        db.ForeignKey('documents.id'), 
        nullable=False
    )
    event_type = db.Column(db.String(50), nullable=False)
    event_name = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.String(50))
    end_time = db.Column(db.String(50))
    duration = db.Column(db.String(20))
    location = db.Column(db.String(255))
    remarks = db.Column(db.Text)
    confidence = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event': self.event_name,
            'event_type': self.event_type,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'location': self.location,
            'remarks': self.remarks,
            'confidence': self.confidence
        }
