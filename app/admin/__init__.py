# app/admin/__init__.py

from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

from . import routes  # <-- załaduj trasy blueprinta

