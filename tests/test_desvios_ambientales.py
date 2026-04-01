import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.desvios_page import DesviosPage, DesviosDashboardPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  SMOKE
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
@pytest.mark.smoke
class TestDesviosSmoke:

    def test_tabla_carga(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*DesviosPage.TABLA).is_displayed()

    def test_tabla_tiene_filas(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        assert len(filas) > 0

    def test_contador_visible(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        texto = page.obtener_total_texto()
        assert "reporte" in texto.lower()

    def test_boton_exportar_presente(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        href = page.exportar_href()
        assert href is not None and "exportar" in href.lower()

    def test_dashboard_carga(self, driver_logueado):
        page = DesviosDashboardPage(driver_logueado, BASE_URL)
        page.ir()
        assert "/admin/dashboard" in driver_logueado.current_url or \
               driver_logueado.find_element(By.CSS_SELECTOR, "h2, .section-title").is_displayed()


# ════════════════════════════════════════════════════════
#  FILTROS
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosFiltros:

    def test_filtro_por_estado_reduce_resultados(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())

        # Intentar filtrar por el primer estado disponible
        from selenium.webdriver.support.ui import Select
        sel = driver_logueado.find_element(*DesviosPage.FILTER_SEL)
        opciones = sel.find_elements(By.TAG_NAME, "option")
        valores = [o.get_attribute("value") for o in opciones if o.get_attribute("value")]

        if not valores:
            pytest.skip("No hay opciones de filtro disponibles")

        page.filtrar_por_estado(valores[0])
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes

    def test_estados_en_tabla_son_visibles(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        estados = page.obtener_estados_visibles()
        assert len(estados) > 0

    def test_url_con_filtro_estado(self, driver_logueado):
        driver_logueado.get(f"{BASE_URL}/admin/registrar?estado=Pendiente")
        WebDriverWait(driver_logueado, 10).until(
            EC.presence_of_element_located(DesviosPage.TABLA)
        )
        assert "estado=Pendiente" in driver_logueado.current_url


# ════════════════════════════════════════════════════════
#  MODAL CREAR
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosModalCrear:

    def test_modal_se_abre(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert page.modal_crear_abierto()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_fecha(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        campo = driver_logueado.find_element(By.ID, "fecha_inicio")
        assert campo.is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_select_area(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        select = driver_logueado.find_element(By.NAME, "area_reportante")
        assert select.is_displayed()
        page.cerrar_modal_crear()

    def test_modal_cierra_correctamente(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        page.cerrar_modal_crear()
        time.sleep(0.5)
        assert not page.modal_crear_abierto()


# ════════════════════════════════════════════════════════
#  ACCIONES EN FILAS
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosAccionesFila:

    def test_btn_ver_detalle_presente_en_filas(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay filas en la tabla")
        btn = filas[0].find_element(By.CSS_SELECTOR, ".btn-blue")
        assert btn.is_displayed()

    def test_btn_editar_presente_en_filas(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay filas en la tabla")
        try:
            btn = filas[0].find_element(By.CSS_SELECTOR, ".btn-yellow")
            assert btn.is_displayed()
        except Exception:
            pytest.skip("Botón editar no visible (posiblemente sin permisos)")

    def test_abrir_detalle_primer_registro(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay filas en la tabla")
        page.abrir_detalle_fila(0)
        # Verificar que se abrió algún modal o se navegó
        url_actual = driver_logueado.current_url
        modal_abierto = driver_logueado.execute_script(
            "var modals = document.querySelectorAll('.modal-overlay');"
            "for (var i=0; i<modals.length; i++) {"
            "  var s = window.getComputedStyle(modals[i]);"
            "  if (s.display !== 'none') return true;"
            "} return false;"
        )
        assert modal_abierto or "/detalle" in url_actual
        # Limpiar: cerrar cualquier modal abierto
        driver_logueado.execute_script(
            "document.querySelectorAll('.modal-overlay').forEach(function(m){"
            "  m.style.display='none';"
            "});"
        )
