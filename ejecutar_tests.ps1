# ════════════════════════════════════════════════════════
#  Script para ejecutar los tests de RegistroMineria
# ════════════════════════════════════════════════════════

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  EJECUTANDO TESTS - RegistroMineria                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "venv")) {
    Write-Host "✗ Error: No se encuentra el entorno virtual 'venv'" -ForegroundColor Red
    Write-Host "  Asegúrate de estar en el directorio RegistroMineria" -ForegroundColor Yellow
    exit 1
}

# Verificar que el servidor esté corriendo
Write-Host "→ Verificando servidor Flask..." -ForegroundColor Yellow
$response = $null
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8080" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host "✓ Servidor Flask está corriendo en http://127.0.0.1:8080" -ForegroundColor Green
} catch {
    Write-Host "✗ El servidor Flask NO está corriendo" -ForegroundColor Red
    Write-Host "  Inicia el servidor con: python app.py" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n→ Ejecutando tests (esto puede tomar 3-4 minutos)...`n" -ForegroundColor Yellow

# Ejecutar tests
.\venv\Scripts\python.exe -m pytest tests/ -v --tb=short

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TESTS COMPLETADOS                                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
