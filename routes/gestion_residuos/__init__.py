from flask import Blueprint

gr_bp = Blueprint('gr', __name__)

from routes.gestion_residuos import dashboard
from routes.gestion_residuos import generacion
from routes.gestion_residuos import comercializable
from routes.gestion_residuos import matpel
from routes.gestion_residuos import compostaje
from routes.gestion_residuos import exportar
