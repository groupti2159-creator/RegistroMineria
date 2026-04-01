import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.meteorologia_page import MeteorologiaPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  SMOKE
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
@pytest.mark.smoke
class TestMeteorologiaSmoke:

    def test_pagina_carga(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert "/meteorologia/dashboard" in driver_logueado.current_url

    def test_titulo_visible(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        titulo = page.titulo_texto()
        assert titulo != ""

    def test_input_apikey_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.input_apikey_presente()

    def test_input_ciudad_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.input_ciudad_presente()

    def test_boton_conectar_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.btn_conectar_presente()


# ════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE LA API
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
class TestMeteorologiaConfiguracion:

    def test_seccion_configuracion_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.tiene_input_configuracion()

    def test_ciudad_default_tiene_valor(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        campo = driver_logueado.find_element(*MeteorologiaPage.INPUT_CIUDAD)
        valor = campo.get_attribute("value") or campo.get_attribute("placeholder") or ""
        assert valor != ""

    def test_boton_conectar_es_clickeable(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*MeteorologiaPage.BTN_CONECTAR)
        assert btn.is_enabled()

    def test_apikey_input_es_editable(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        campo = driver_logueado.find_element(*MeteorologiaPage.INPUT_APIKEY)
        tipo = campo.get_attribute("type") or "text"
        assert tipo in ("text", "password", "search")
        assert not campo.get_attribute("disabled")


# ════════════════════════════════════════════════════════
#  LAYOUT Y MÉTRICAS
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
class TestMeteorologiaLayout:

    def test_sidebar_visible(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        sidebar = driver_logueado.find_element(By.CSS_SELECTOR, ".sidebar")
        assert sidebar.is_displayed()

    def test_topbar_visible(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        topbar = driver_logueado.find_element(By.CSS_SELECTOR, ".topbar, .top-bar, nav")
        assert topbar.is_displayed()

    def test_contenido_principal_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        contenido = driver_logueado.find_element(By.CSS_SELECTOR, ".main-content, .content, main, #content")
        assert contenido.is_displayed()
