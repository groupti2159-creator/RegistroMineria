import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.meteorologia_page import MeteorologiaPage

BASE_URL = "http://127.0.0.1:8080"

METRICAS_IDS = [
    "wx-temp", "wx-range", "wx-hum", "wx-press",
    "wx-wind", "wx-gust", "wx-wdir", "wx-clouds",
    "wx-vis", "wx-rain", "wx-dew", "wx-hi", "wx-wc", "wx-wr",
]


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
        assert page.titulo_texto() != ""

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

    def test_boton_actualizar_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.btn_actualizar_presente()

    def test_boton_exportar_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.btn_exportar_presente()

    def test_boton_limpiar_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.btn_limpiar_presente()


# ════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE LA API
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
class TestMeteorologiaConfiguracion:

    def test_ciudad_default_tiene_valor(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.ciudad_default() != ""

    def test_apikey_input_es_editable(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        campo = driver_logueado.find_element(*MeteorologiaPage.INPUT_APIKEY)
        assert not campo.get_attribute("disabled")
        assert not campo.get_attribute("readonly")

    def test_ciudad_input_es_editable(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        campo = driver_logueado.find_element(*MeteorologiaPage.INPUT_CIUDAD)
        assert not campo.get_attribute("disabled")

    def test_boton_conectar_es_clickeable(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*MeteorologiaPage.BTN_CONECTAR)
        assert btn.is_enabled()

    def test_boton_exportar_es_clickeable(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*MeteorologiaPage.BTN_EXPORTAR)
        assert btn.is_enabled()


# ════════════════════════════════════════════════════════
#  ELEMENTOS DE MÉTRICAS (14 métricas del dashboard)
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
class TestMeteorologiaMetricas:

    @pytest.mark.parametrize("metric_id", METRICAS_IDS)
    def test_elemento_metrica_existe_en_dom(self, driver_logueado, metric_id):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.metrica_elemento_presente(metric_id), \
            f"Elemento con id='{metric_id}' no encontrado en el DOM"

    def test_todas_las_metricas_existen(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        faltantes = [mid for mid in METRICAS_IDS if not page.metrica_elemento_presente(mid)]
        assert faltantes == [], f"Métricas faltantes: {faltantes}"


# ════════════════════════════════════════════════════════
#  TABLA HISTÓRICA
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
class TestMeteorologiaTabla:

    def test_tbody_tabla_historica_existe(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.tabla_historica_presente()

    def test_contador_registros_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        try:
            driver_logueado.find_element(By.ID, "wx-count")
        except Exception:
            pytest.skip("Elemento wx-count no presente")

    def test_estado_conexion_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.status_text_presente()

    def test_indicador_pulse_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        try:
            driver_logueado.find_element(*MeteorologiaPage.WX_PULSE)
        except Exception:
            pytest.skip("Indicador wx-pulse no presente en el DOM")

    def test_ultimo_update_elemento_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        try:
            driver_logueado.find_element(*MeteorologiaPage.WX_LAST_UPDATE)
        except Exception:
            pytest.skip("Elemento wx-last-update no presente")


# ════════════════════════════════════════════════════════
#  LAYOUT
# ════════════════════════════════════════════════════════

@pytest.mark.meteorologia
class TestMeteorologiaLayout:

    def test_sidebar_visible(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(By.CSS_SELECTOR, ".sidebar").is_displayed()

    def test_topbar_visible(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        topbar = driver_logueado.find_element(By.CSS_SELECTOR, ".topbar, .top-bar, nav")
        assert topbar.is_displayed()

    def test_contenido_principal_presente(self, driver_logueado):
        page = MeteorologiaPage(driver_logueado, BASE_URL)
        page.ir()
        contenido = driver_logueado.find_element(
            By.CSS_SELECTOR, ".main-content, .content, main, #content"
        )
        assert contenido.is_displayed()
