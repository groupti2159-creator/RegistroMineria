from flask import Blueprint

da_bp = Blueprint('da', __name__)

from routes.desvios_ambientales import dashboard
from routes.desvios_ambientales import registro
from routes.desvios_ambientales import detalle
from routes.desvios_ambientales import estadisticas
from routes.desvios_ambientales import exportar
from routes.desvios_ambientales import api_personal
