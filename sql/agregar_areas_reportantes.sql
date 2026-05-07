-- Agregar nuevas áreas reportantes
-- Ejecutar: mysql -u root -p desvios_ambientales < sql/agregar_areas_reportantes.sql

USE desvios_ambientales;

INSERT IGNORE INTO Tbl_AreaReportante (areareportante) VALUES
('GERENCIA DE OPERACIONES'),
('MANTTO ELECTRICO'),
('GEOLOGIA Y EXPLORACION'),
('BIENESTAR SOCIAL'),
('MANTENIMIENTO MECANICO'),
('MINA'),
('OBRAS CIVILES'),
('PLANEAMIENTO'),
('PLANTA'),
('PROYECTOS'),
('RECURSOS HUMANOS'),
('SSOMA'),
('PROTECCION INTERNA');

-- Verificar las áreas insertadas
SELECT * FROM Tbl_AreaReportante ORDER BY areareportante;
