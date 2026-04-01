import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.residuos_page import GeneracionPage, SubpaginaResiduosPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  SMOKE — generación diaria
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
@pytest.mark.smoke
class TestGeneracionSmoke:

    def test_pagina_carga(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert "/residuos/generacion" in driver_logueado.current_url

    def test_tabla_generacion_visible(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        tabla = driver_logueado.find_element(*GeneracionPage.TABLA)
        assert tabla.is_displayed()

    def test_boton_nuevo_visible(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*GeneracionPage.BTN_NUEVO)
        assert btn.is_displayed()

    def test_tabla_tiene_columna_fecha(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        headers = driver_logueado.find_elements(By.CSS_SELECTOR, ".gen-table thead th")
        textos = [h.text.strip().upper() for h in headers]
        assert any("FECHA" in t for t in textos)

    def test_tabla_tiene_columna_generacion(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        headers = driver_logueado.find_elements(By.CSS_SELECTOR, ".gen-table thead th")
        textos = [h.text.strip().upper() for h in headers]
        assert any("GEN" in t or "DIARIA" in t for t in textos)


# ════════════════════════════════════════════════════════
#  MODAL NUEVO REGISTRO
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
class TestGeneracionModal:

    def test_modal_se_abre(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_nuevo()
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_modal_tiene_campo_fecha(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_nuevo()
        # Buscar campo de fecha dentro del modal
        campos_fecha = driver_logueado.find_elements(By.CSS_SELECTOR, "#modal-overlay input[type='date']")
        assert len(campos_fecha) > 0
        page.cerrar_modal()

    def test_modal_cierra_correctamente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_nuevo()
        page.cerrar_modal()
        time.sleep(0.5)
        assert not page.modal_abierto()


# ════════════════════════════════════════════════════════
#  FILTROS DE FECHA
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
class TestGeneracionFiltros:

    def test_filtro_fecha_desde_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        campo = driver_logueado.find_element(*GeneracionPage.FILTRO_DESDE)
        assert campo.is_displayed()

    def test_filtro_fecha_hasta_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        campo = driver_logueado.find_element(*GeneracionPage.FILTRO_HASTA)
        assert campo.is_displayed()

    def test_boton_filtrar_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*GeneracionPage.BTN_FILTRAR)
        assert btn.is_displayed()

    def test_filtrar_por_rango_fecha(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.filtrar_fechas("2025-01-01", "2025-12-31")
        time.sleep(0.5)
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes
        page.limpiar_filtros()

    def test_boton_exportar_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*GeneracionPage.BTN_EXPORTAR)
        assert btn.is_displayed()


# ════════════════════════════════════════════════════════
#  ACCIONES EN FILAS
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
class TestGeneracionAccionesFila:

    def test_filas_tienen_boton_ver(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros de generación")
        btn = filas[0].find_element(By.CSS_SELECTOR, ".btn-ver")
        assert btn.is_displayed()

    def test_filas_tienen_boton_editar(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros de generación")
        btn = filas[0].find_element(By.CSS_SELECTOR, ".btn-edit")
        assert btn.is_displayed()

    def test_ver_detalle_abre_modal(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros de generación")
        page.ver_detalle_fila(0)
        modal_abierto = driver_logueado.execute_script(
            "var id = 'modal-detalle-overlay';"
            "var el = document.getElementById(id);"
            "if (!el) return false;"
            "return window.getComputedStyle(el).display !== 'none';"
        )
        assert modal_abierto
        driver_logueado.execute_script(
            "var el = document.getElementById('modal-detalle-overlay');"
            "if (el) el.style.display = 'none';"
        )


# ════════════════════════════════════════════════════════
#  SMOKE — subpáginas (comercializable, compostaje, matpel)
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
@pytest.mark.smoke
class TestSubpaginasSmoke:

    def test_comercializable_carga(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        assert page.tabla_visible() or driver_logueado.find_element(
            By.CSS_SELECTOR, ".section-title, h2"
        ).is_displayed()

    def test_compostaje_carga(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        assert driver_logueado.find_element(By.CSS_SELECTOR, ".section-title, h2").is_displayed()

    def test_matpel_carga(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        assert driver_logueado.find_element(By.CSS_SELECTOR, ".section-title, h2").is_displayed()

    def test_comercializable_tiene_boton_nuevo(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        assert page.btn_nuevo_visible()

    def test_compostaje_tiene_boton_nuevo(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        assert page.btn_nuevo_visible()

    def test_matpel_tiene_boton_nuevo(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        assert page.btn_nuevo_visible()
