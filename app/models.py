from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' or 'user'
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


class ZendeskSettings(db.Model):
    """Store Zendesk API credentials and settings"""
    __tablename__ = 'zendesk_settings'

    id = db.Column(db.Integer, primary_key=True)
    subdomain = db.Column(db.String(100))
    email = db.Column(db.String(120))
    api_token = db.Column(db.String(256))  # Consider encrypting this in production
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    @staticmethod
    def get_active_settings():
        """Get the active Zendesk settings"""
        return ZendeskSettings.query.filter_by(is_active=True).first()

    def __repr__(self):
        return f'<ZendeskSettings {self.subdomain}>'


class Job(db.Model):
    """Model for tracking asynchronous background jobs"""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(255), unique=True, nullable=False, index=True)  # Celery task ID
    tool_slug = db.Column(db.String(100), nullable=False, index=True)  # Which tool created this job
    status = db.Column(db.String(20), default='pending', index=True)  # pending, running, completed, failed, cancelled
    progress = db.Column(db.Integer, default=0)  # Progress percentage 0-100
    total_items = db.Column(db.Integer, default=0)  # Total number of items to process
    processed_items = db.Column(db.Integer, default=0)  # Number of items processed so far
    result_data = db.Column(db.Text)  # JSON string of final results
    error_message = db.Column(db.Text)  # Error message if failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)  # When job actually started processing
    completed_at = db.Column(db.DateTime)  # When job finished (success or failure)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('jobs', lazy='dynamic'))

    def __repr__(self):
        return f'<Job {self.job_id} ({self.status})>'

    @staticmethod
    def create_job(job_id, tool_slug, total_items, user_id):
        """
        Create a new job record.

        Args:
            job_id: Celery task ID
            tool_slug: Tool identifier
            total_items: Total number of items to process
            user_id: User who created the job

        Returns:
            Job instance
        """
        job = Job(
            job_id=job_id,
            tool_slug=tool_slug,
            total_items=total_items,
            user_id=user_id,
            status='pending',
            progress=0,
            processed_items=0
        )
        db.session.add(job)
        db.session.commit()
        return job

    def update_progress(self, processed_items, status='running'):
        """
        Update job progress.

        Args:
            processed_items: Number of items processed
            status: Current job status
        """
        self.processed_items = processed_items
        self.status = status

        if self.total_items > 0:
            self.progress = int((processed_items / self.total_items) * 100)
        else:
            self.progress = 0

        if status == 'running' and not self.started_at:
            self.started_at = datetime.utcnow()

        db.session.commit()

    def complete(self, result_data=None, status='completed'):
        """
        Mark job as completed.

        Args:
            result_data: Dict of results to store as JSON
            status: Final status ('completed' or 'failed')
        """
        self.status = status
        self.progress = 100 if status == 'completed' else self.progress
        self.completed_at = datetime.utcnow()

        if result_data:
            self.result_data = json.dumps(result_data)

        db.session.commit()

    def fail(self, error_message):
        """
        Mark job as failed.

        Args:
            error_message: Error message string
        """
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def cancel(self):
        """Mark job as cancelled"""
        self.status = 'cancelled'
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def get_result(self):
        """
        Get result data as dict.

        Returns:
            Dict of results or None
        """
        if self.result_data:
            try:
                return json.loads(self.result_data)
            except json.JSONDecodeError:
                return None
        return None

    def get_elapsed_time(self):
        """
        Get elapsed time for the job.

        Returns:
            String representation of elapsed time
        """
        if self.completed_at:
            delta = self.completed_at - self.created_at
        elif self.started_at:
            delta = datetime.utcnow() - self.started_at
        else:
            return "Not started"

        minutes, seconds = divmod(int(delta.total_seconds()), 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
