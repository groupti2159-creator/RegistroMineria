from flask import Blueprint

supervisor_bp = Blueprint('supervisor', __name__)

from routes.core.supervisor import registro
from routes.core.supervisor import notificaciones
