"""
Database models for HR Portal
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model):
    """User model for HR Portal."""
    __tablename__ = 'users'
    
    username = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Applicant')
    full_name = db.Column(db.String(255), nullable=False)
    mobile_number = db.Column(db.String(20))
    employee_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='creator', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password = hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """Verify password."""
        return self.password == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'mobile_number': self.mobile_number,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Ticket(db.Model):
    """Ticket model for submissions."""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Feedback, Complaint, Suggestion
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending Review')  # Pending Review, Action Taken, Resolved
    hr_notes = db.Column(db.Text, default='No response yet')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'type': self.type,
            'subject': self.subject,
            'description': self.description,
            'status': self.status,
            'hr_notes': self.hr_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
