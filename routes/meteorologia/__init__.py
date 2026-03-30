from flask import Blueprint

meteorologia_bp = Blueprint('meteorologia', __name__)

from routes.meteorologia import dashboard
from routes.meteorologia import informacion
