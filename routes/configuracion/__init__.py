from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from routes.configuracion import dashboard
from routes.configuracion import usuarios
from routes.configuracion import roles
