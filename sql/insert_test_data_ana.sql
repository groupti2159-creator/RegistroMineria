-- ════════════════════════════════════════════════════════
--  Script para insertar datos de prueba en Reporte ANA
-- ════════════════════════════════════════════════════════

-- Insertar registros de prueba en tbl_registroana
INSERT INTO tbl_registroana 
(Fecha, TiempoOperacion, ContometroInicial, ContometroFinal, VolumenM3, CaudalM3S, FechaRegistro)
VALUES
-- Enero 2026
('2026-01-15', '24 horas', 14500.00, 14508.50, 8.50, 0.000098380, NOW()),
('2026-01-16', '24 horas', 14508.50, 14517.20, 8.70, 0.000100694, NOW()),
('2026-01-17', '24 horas', 14517.20, 14525.80, 8.60, 0.000099537, NOW()),

-- Febrero 2026
('2026-02-10', '24 horas', 14600.00, 14608.92, 8.92, 0.000103241, NOW()),
('2026-02-11', '24 horas', 14608.92, 14617.50, 8.58, 0.000099306, NOW()),
('2026-02-12', '24 horas', 14617.50, 14626.10, 8.60, 0.000099537, NOW()),

-- Marzo 2026
('2026-03-05', '24 horas', 14700.00, 14708.75, 8.75, 0.000101273, NOW()),
('2026-03-06', '24 horas', 14708.75, 14717.40, 8.65, 0.000100116, NOW()),
('2026-03-07', '24 horas', 14717.40, 14726.00, 8.60, 0.000099537, NOW()),
('2026-03-08', '24 horas', 14726.00, 14734.80, 8.80, 0.000101852, NOW());

-- Verificar los datos insertados
SELECT 
    IdRegistroANA,
    Fecha,
    TiempoOperacion,
    ContometroInicial,
    ContometroFinal,
    VolumenM3,
    CaudalM3S,
    FechaRegistro
FROM tbl_registroana
ORDER BY Fecha DESC
LIMIT 10;
