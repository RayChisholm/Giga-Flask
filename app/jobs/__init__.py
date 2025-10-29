"""
Jobs blueprint for monitoring asynchronous background jobs.
"""

from flask import Blueprint

jobs_bp = Blueprint('jobs', __name__, template_folder='templates')

# Import routes here so they're registered with the blueprint
# Note: This may cause circular imports if not careful
from . import routes
