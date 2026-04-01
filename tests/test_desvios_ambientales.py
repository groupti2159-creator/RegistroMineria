import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.desvios_page import DesviosPage, DesviosDashboardPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  SMOKE
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
@pytest.mark.smoke
class TestDesviosSmoke:

    def test_pagina_registrar_carga(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*DesviosPage.TABLA).is_displayed()

    def test_tabla_tiene_filas(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert len(page.obtener_filas()) > 0

    def test_contador_reportes_visible(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert "reporte" in page.obtener_total_texto().lower()

    def test_boton_nuevo_visible(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*DesviosPage.BTN_NUEVO).is_displayed()

    def test_boton_exportar_tiene_href(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert "exportar" in page.exportar_href().lower()

    def test_dashboard_carga(self, driver_logueado):
        page = DesviosDashboardPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.carga_correctamente()


# ════════════════════════════════════════════════════════
#  TABLA Y FILTROS
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosFiltros:

    def test_filtro_estado_tiene_opciones(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        assert len(page.opciones_estado()) > 0

    def test_filtrar_por_estado_reduce_resultados(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        opciones = page.opciones_estado()
        if not opciones:
            pytest.skip("No hay opciones de filtro")
        page.filtrar_por_estado(opciones[0])
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes

    def test_url_filtro_estado_pendiente(self, driver_logueado):
        driver_logueado.get(f"{BASE_URL}/admin/registrar?estado=Pendiente")
        WebDriverWait(driver_logueado, 10).until(
            EC.presence_of_element_located(DesviosPage.TABLA)
        )
        assert "estado=Pendiente" in driver_logueado.current_url

    def test_estados_badges_visibles_en_tabla(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        estados = page.obtener_estados_visibles()
        assert len(estados) > 0

    def test_columnas_tabla_correctas(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        headers = driver_logueado.find_elements(By.CSS_SELECTOR, ".data-table thead th")
        textos = " ".join(h.text.upper() for h in headers)
        assert "FECHA" in textos
        assert "ESTADO" in textos

    def test_paginacion_visible_si_hay_mas_de_una_pagina(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        total_texto = page.obtener_total_texto()
        try:
            total = int(''.join(filter(str.isdigit, total_texto.split()[0])))
        except Exception:
            pytest.skip("No se pudo obtener el total")
        if total > 10:
            paginacion = driver_logueado.find_elements(By.CSS_SELECTOR, ".pagination")
            assert len(paginacion) > 0


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

    def test_modal_tiene_campo_fecha_inicio(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(By.ID, "fecha_inicio").is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_fecha_ejecucion(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(By.NAME, "fecha_ejecucion").is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_select_area_reportante(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        sel = driver_logueado.find_element(*DesviosPage.SEL_AREA_REP)
        opciones = sel.find_elements(By.TAG_NAME, "option")
        assert len(opciones) > 1
        page.cerrar_modal_crear()

    def test_modal_tiene_select_ubicacion(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        sel = driver_logueado.find_element(*DesviosPage.SEL_UBICACION)
        assert sel.is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_descripcion(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(*DesviosPage.CAMPO_DESCRIPCION).is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_personal_responsable(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(*DesviosPage.CAMPO_PERSONAL).is_displayed()
        page.cerrar_modal_crear()

    def test_modal_cierra_correctamente(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        page.cerrar_modal_crear()
        time.sleep(0.5)
        assert not page.modal_crear_abierto()

    def test_modal_tiene_boton_guardar(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        btn = driver_logueado.find_element(By.ID, "btnGuardarReporte")
        assert btn.is_displayed()
        page.cerrar_modal_crear()

    def test_crear_registro_completo(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.abrir_modal_crear()
        page.llenar_form_crear(
            fecha="2026-03-31",
            descripcion=f"Test Selenium {int(time.time())}",
            accion="Accion correctiva test",
            personal="Juan Test",
            dni="99999999"
        )
        page.enviar_form_crear()
        page.ir()
        assert len(page.obtener_filas()) >= filas_antes


# ════════════════════════════════════════════════════════
#  MODAL DETALLE
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosModalDetalle:

    def test_modal_detalle_se_abre(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.abrir_modal_detalle(0)
        assert page.modal_detalle_abierto()
        page.cerrar_modal_detalle()

    def test_modal_detalle_muestra_informacion(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.abrir_modal_detalle(0)
        contenido = driver_logueado.find_element(
            By.CSS_SELECTOR, "#modalDetalle .modal-body, #modalDetalle"
        ).text
        assert contenido.strip() != ""
        page.cerrar_modal_detalle()

    def test_modal_detalle_cierra(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.abrir_modal_detalle(0)
        page.cerrar_modal_detalle()
        time.sleep(0.5)
        assert not page.modal_detalle_abierto()


# ════════════════════════════════════════════════════════
#  MODAL EDITAR
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosModalEditar:

    def test_modal_editar_se_abre(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.abrir_modal_editar(0)
        assert page.modal_editar_abierto()
        page.cerrar_modal_editar()

    def test_modal_editar_trae_datos_precargados(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.abrir_modal_editar(0)
        valor_fecha = page.edit_campo_valor("edit_fecha")
        assert valor_fecha != ""
        page.cerrar_modal_editar()

    def test_modal_editar_cierra(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.abrir_modal_editar(0)
        page.cerrar_modal_editar()
        time.sleep(0.5)
        assert not page.modal_editar_abierto()


# ════════════════════════════════════════════════════════
#  ELIMINAR
# ════════════════════════════════════════════════════════

@pytest.mark.desvios
class TestDesviosEliminar:

    def test_boton_eliminar_presente_en_filas(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        btn = filas[0].find_element(By.CSS_SELECTOR, ".btn-icon-danger")
        assert btn.is_displayed()

    def test_eliminar_reduce_conteo(self, driver_logueado):
        page = DesviosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay registros para eliminar")
        page.click_eliminar_fila(0)
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)
