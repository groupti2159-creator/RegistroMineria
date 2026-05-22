from flask import Blueprint

api_bp = Blueprint('api', __name__)

from routes.api.cambiar_contrasena import *
