from flask import Blueprint

proyectos_bp = Blueprint('proyectos', __name__)

from routes.core.proyectos import selector
