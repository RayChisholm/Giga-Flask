from flask import Blueprint

tools_bp = Blueprint('tools', __name__)

from app.tools import routes
