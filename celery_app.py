"""
Celery application for async task processing.

To start the Celery worker:
    celery -A celery_app worker --loglevel=info

To start Flower monitoring (optional):
    celery -A celery_app flower
"""

from celery import Celery
import os

# Get broker and backend from environment or use defaults
broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery instance without Flask app initially
celery = Celery(
    'tasks',
    broker=broker_url,
    backend=result_backend
)

# Load configuration from CeleryConfig class (lazy import to avoid circular deps)
def configure_celery():
    from app.celery_config import CeleryConfig
    celery.config_from_object(CeleryConfig)

# Configure celery on first use
configure_celery()


def init_celery(app):
    """
    Initialize Celery with Flask app context.

    This should be called from within the Flask app factory.
    """
    # Store the app for use in tasks
    celery.app = app

    # Ensure tasks run within Flask application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Load tasks when running as Celery worker
# Import Flask app to register tasks
try:
    from app import create_app
    flask_app = create_app()
    init_celery(flask_app)

    # Import tasks to register them
    from app.tasks import zendesk_tasks
except ImportError as e:
    print(f"Warning: Could not import tasks: {e}")
except Exception as e:
    print(f"Warning: Error initializing Celery with Flask: {e}")
