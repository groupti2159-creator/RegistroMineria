from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from routes.core.auth import login
from routes.core.auth import seleccionar_rol
from routes.core.auth import logout
