from flask import Blueprint, render_template, request
from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec
from extensions import mysql
from decimal import Decimal
from datetime import date, datetime

gr_bp = Blueprint('gr', __name__)

# Secciones con su columna coripuno
SECTIONS_CP = [
    {"id": "gen",  "label": "RRSS Generales",        "unit": "Kg",  "col": "gen_coripuno"},
    {"id": "org",  "label": "RRSS Orgánicos",         "unit": "Kg",  "col": "org_coripuno"},
    {"id": "ind",  "label": "RRSS Industriales",      "unit": "Kg",  "col": "ind_coripuno"},
    {"id": "hosp", "label": "Hospitalarios",          "unit": "Kg",  "col": "hosp_coripuno"},
    {"id": "ace",  "label": "Aceites",                "unit": "gal", "col": "ace_coripuno"},
    {"id": "bor",  "label": "Borras",                 "unit": "Kg",  "col": "bor_coripuno"},
    {"id": "cop",  "label": "Copelas",                "unit": "Kg",  "col": "cop_coripuno"},
    {"id": "tier", "label": "Tierra contaminada",     "unit": "Kg",  "col": "tier_coripuno"},
    {"id": "var",  "label": "Varios",                 "unit": "Kg",  "col": "var_coripuno"},
    {"id": "tar",  "label": "Tarros y res. menores",  "unit": "Kg",  "col": "tar_coripuno"},
    {"id": "chat", "label": "Chatarra mayor",         "unit": "Kg",  "col": "chat_coripuno"},
    {"id": "plas", "label": "RRSS Plástico",          "unit": "Kg",  "col": "plas_coripuno"},
    {"id": "vid",  "label": "RRSS Vidrio",            "unit": "Kg",  "col": "vid_coripuno"},
    {"id": "pap",  "label": "RRSS Papel y cartón",    "unit": "Kg",  "col": "pap_coripuno"},
    {"id": "mad",  "label": "RRSS Madera",            "unit": "Kg",  "col": "mad_coripuno"},
]

def _serialize(v):
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, (date, datetime)): return v.isoformat()
    return v

@gr_bp.route('/residuos/dashboard')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()
    cols = ", ".join(["fecha"] + [s["col"] for s in SECTIONS_CP])
    cur.execute(f"SELECT {cols} FROM tbl_generacion_diaria ORDER BY fecha DESC")
    rows = cur.fetchall() or []
    cur.close()

    # Convertir a lista de dicts serializables
    keys = ["fecha"] + [s["col"] for s in SECTIONS_CP]
    registros = []
    for row in rows:
        if isinstance(row, dict):
            r = {k.lower(): _serialize(v) for k, v in row.items()}
        else:
            r = {keys[i]: _serialize(row[i]) for i in range(len(keys))}
        # total kg CORI PUNO (sin aceites)
        r['total_cp'] = sum(
            float(r.get(s["col"], 0) or 0)
            for s in SECTIONS_CP if s["unit"] == "Kg"
        )
        registros.append(r)

    return render_template(
        'gestion_residuos/dashboard.html',
        notif_count=get_notif_count(),
        sections=SECTIONS_CP,
        registros=registros,
    )

@gr_bp.route('/residuos/comercializable')
@admin_required
@modulo_required('COMERCIALIZABLE')
def comercializable():
    return render_template('gestion_residuos/comercializable.html', notif_count=get_notif_count())

@gr_bp.route('/residuos/matpel')
@admin_required
@modulo_required('DISPOSICION_MATPEL')
def matpel():
    return render_template('gestion_residuos/matpel.html', notif_count=get_notif_count())

@gr_bp.route('/residuos/compostaje')
@admin_required
@modulo_required('COMPOSTAJE')
def compostaje():
    return render_template('gestion_residuos/compostaje.html', notif_count=get_notif_count())
