-- Crear tabla tbl_rolmodulo para gestión de permisos por rol
-- Esta tabla vincula roles con módulos (permisos)

CREATE TABLE IF NOT EXISTS tbl_rolmodulo (
    idrolmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idroles INT NOT NULL,
    idmodulo INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_rol_modulo (idroles, idmodulo),
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles) ON DELETE CASCADE,
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices para mejorar rendimiento
CREATE INDEX idx_idroles ON tbl_rolmodulo(idroles);
CREATE INDEX idx_idmodulo ON tbl_rolmodulo(idmodulo);

-- Verificar que se creó correctamente
SELECT 'Tabla tbl_rolmodulo creada exitosamente' as resultado;
DESCRIBE tbl_rolmodulo;
