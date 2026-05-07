from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    
    # Crear tabla
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tbl_riesgos_criticos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo VARCHAR(10) NOT NULL,
            descripcion VARCHAR(500) NOT NULL,
            tipo_asociado INT NOT NULL COMMENT '1=SEGURIDAD, 2=MEDIO AMBIENTE',
            activo TINYINT(1) DEFAULT 1,
            FOREIGN KEY (tipo_asociado) REFERENCES tbl_descripciontipo(iddescripciontipo),
            INDEX idx_tipo (tipo_asociado),
            INDEX idx_activo (activo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    # Riesgos de SEGURIDAD
    seguridad = [
        ('RC 01', 'DESPRENDIMIENTO DE ROCAS / INESTABILIDAD GEOMECÁNICA'),
        ('RC 02', 'ATMÓSFERAS PELIGROSAS (GASES TÓXICOS / DEFICIENCIA DE O₂)'),
        ('RC 03', 'FALLA DE VENTILACIÓN (ACUMULACIÓN DE GASES / HUMO / POLVO)'),
        ('RC 04', 'CONTACTO CON ENERGÍA ELÉCTRICA (ELECTROCUCIÓN / ARCO ELÉCTRICO)'),
        ('RC 05', 'ENERGÍAS PELIGROSAS – LOTO (LIBERACIÓN INESPERADA DE ENERGÍA)'),
        ('RC 06', 'CAÍDA DE PERSONAS AL MISMO NIVEL'),
        ('RC 07', 'CAÍDA DE PERSONAS A DIFERENTE NIVEL (ALTURA / ABERTURAS / HUECOS)'),
        ('RC 08', 'VOLCADURA DE EQUIPOS / VEHÍCULOS'),
        ('RC 09', 'COLISIÓN / ATROPELLO / INTERACCIÓN PERSONA–EQUIPO MÓVIL'),
        ('RC 10', 'ATRAPAMIENTO / APRISIONAMIENTO POR PARTES EN MOVIMIENTO'),
        ('RC 11', 'GOLPEADO POR OBJETOS (CAÍDA / PROYECCIÓN / CARGA SUSPENDIDA)'),
        ('RC 12', 'IZAJE Y MANIOBRAS (FALLA DE ESLINGAS / CARGA SUSPENDIDA)'),
        ('RC 13', 'MANIPULACIÓN DE MATERIALES (APLASTAMIENTO / SOBREESFUERZO / CORTES)'),
        ('RC 14', 'ESPACIOS CONFINADOS (ASFIXIA / INTOXICACIÓN / RESCATE FALLIDO)'),
        ('RC 15', 'EXPLOSIVOS Y VOLADURA (DETONACIÓN / MISFIRE / FLYROCK)'),
        ('RC 16', 'INCENDIO (EQUIPOS, TALLER, ALMACENES, SUBTERRÁNEA)'),
        ('RC 17', 'SUSTANCIAS PELIGROSAS / QUÍMICOS (QUEMADURAS / INTOXICACIÓN / DERRAMES)'),
        ('RC 18', 'TRABAJO EN CALIENTE (SOLDADURA / OXICORTE / CHISPAS)'),
        ('RC 19', 'ALTA PRESIÓN (HIDRÁULICA / NEUMÁTICA – LATIGAZO / INYECCIÓN)'),
        ('RC 20', 'EXCAVACIONES / ZANJAS / COLAPSO DE TALUDES (OBRAS CIVILES)'),
        ('RC 21', 'AHOGAMIENTO / INUNDACIÓN (POZAS / DRENAJES / LLUVIAS)'),
        ('RC 22', 'FATIGA Y SOMNOLENCIA (ERROR HUMANO CRÍTICO / CONDUCCIÓN)'),
        ('RC 23', 'ERGONOMÍA / POSTURAS FORZADAS (LESIONES MÚSCULO-ESQUELÉTICAS / EXPOSICIÓN A TEMPERATURAS EXTREMAS)'),
        ('RC 24', 'INTOXICACIÓN ALIMENTARIA'),
        ('RC 25', 'OTROS (ESPECIFICAR)')
    ]
    
    # Riesgos de MEDIO AMBIENTE
    medio_ambiente = [
        ('MA 01', 'DISPOSICIÓN RESIDUOS'),
        ('MA 02', 'SEGREGACIÓN DE RESIDUOS'),
        ('MA 03', 'DISPOSICIÓN DESMONTE-ESCOMBROS'),
        ('MA 04', 'DISPOSICIÓN RESIDUOS PELIGROSOS'),
        ('MA 05', 'LIXIVIADOS'),
        ('MA 06', 'LODO'),
        ('MA 07', 'OLORES'),
        ('MA 08', 'POLVO'),
        ('MA 09', 'POTENCIAL COLAPSO DE LA PRESA DE RELAVE'),
        ('MA 10', 'DERRAME DE HIDROCARBUROS'),
        ('MA 11', 'DERRAME DE PULPA DE RELAVE'),
        ('MA 12', 'DESCARGA DE AGUAS SIN TRATAMIENTO - EFLUENTES'),
        ('MA 13', 'EMISIÓN DE GASES TÓXICOS'),
        ('MA 14', 'EXPLOSIÓN'),
        ('MA 15', 'INCENDIO'),
        ('MA 16', 'RUIDO'),
        ('MA 17', 'VIBRACIÓN'),
        ('MA 18', 'INCUMPLIMIENTO DE IGA'),
        ('MA 19', 'CONTAMINACIÓN DE SUELO'),
        ('MA 20', 'DERRAME DE PRODUCTOS QUÍMICOS'),
        ('MA 21', 'SISTEMAS HIDRÁULICOS'),
        ('MA 22', 'CONTAMINACIÓN DEL AIRE'),
        ('MA 23', 'DISPOSICIÓN DE RAEEs'),
        ('MA 24', 'DISPOSICIÓN DE NFU')
    ]
    
    print("Insertando riesgos de SEGURIDAD...")
    for codigo, desc in seguridad:
        cur.execute("INSERT INTO tbl_riesgos_criticos (codigo, descripcion, tipo_asociado) VALUES (%s, %s, 1)", (codigo, desc))
    
    print("Insertando riesgos de MEDIO AMBIENTE...")
    for codigo, desc in medio_ambiente:
        cur.execute("INSERT INTO tbl_riesgos_criticos (codigo, descripcion, tipo_asociado) VALUES (%s, %s, 2)", (codigo, desc))
    
    mysql.connection.commit()
    
    cur.execute("SELECT tipo_asociado, COUNT(*) as total FROM tbl_riesgos_criticos GROUP BY tipo_asociado")
    print("\n=== RIESGOS CRÍTICOS CREADOS ===")
    for row in cur.fetchall():
        tipo = "SEGURIDAD" if row['tipo_asociado'] == 1 else "MEDIO AMBIENTE"
        print(f"  {tipo}: {row['total']} riesgos")
    
    cur.close()
    print("\n✅ Completado")
