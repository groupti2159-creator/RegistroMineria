# ════════════════════════════════════════════════════════
#  ecoSupervisor — tests/conftest.py
#  Configuración global de Selenium: driver + login
# ════════════════════════════════════════════════════════

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ── Configuración del entorno ────────────────────────────
BASE_URL  = "http://127.0.0.1:8080"
DNI       = "12345678"    # admin
PASSWORD  = "admin123"    # contraseña del admin
HEADLESS  = False         # False = ves el navegador abrirse


@pytest.fixture(scope="session")
def driver():
    """Driver Chrome compartido para toda la sesión."""
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")

    service = Service(ChromeDriverManager().install())
    drv     = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(8)

    yield drv

    drv.quit()


@pytest.fixture(scope="session")
def driver_logueado(driver):
    """Driver ya autenticado — hace login una sola vez."""
    from tests.pages.login_page import LoginPage

    login = LoginPage(driver, BASE_URL)
    login.ir()
    login.iniciar_sesion(DNI, PASSWORD)

    assert "/login" not in driver.current_url, \
        f"Login falló. URL actual: {driver.current_url}"

    return driver