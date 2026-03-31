from flask import Blueprint

shared_bp = Blueprint('shared', __name__)

from routes.core.shared import notificaciones
