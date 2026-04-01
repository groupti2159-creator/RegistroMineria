import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.aguas_page import MonitoreoPage, ReporteANAPage

BASE_URL = "http://127.0.0.1:8080"


def _modal_abierto(driver, modal_id):
    try:
        return driver.execute_script(
            "var el = document.getElementById(arguments[0]);"
            "if (!el) return false;"
            "var style = window.getComputedStyle(el);"
            "return style.display !== 'none' && style.opacity !== '0';",
            modal_id
        )
    except Exception:
        return False


def _esperar_modal(driver, modal_id, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: _modal_abierto(d, modal_id))


def _cualquier_modal_abierto(driver, modal_ids):
    """Retorna True si cualquiera de los IDs dados está visible."""
    for mid in modal_ids:
        if _modal_abierto(driver, mid):
            return True
    return False


# ════════════════════════════════════════════════════════
#  SMOKE
# ════════════════════════════════════════════════════════

@pytest.mark.aguas
@pytest.mark.smoke
class TestMonitoreoTabla:

    def test_tabla_efluentes_carga(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*MonitoreoPage.TABLA).is_displayed()

    def test_cambiar_tipo_a_ptard(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("ptard")
        assert driver_logueado.find_element(By.ID, "tabla-ptard").is_displayed()

    def test_cambiar_tipo_a_ptap(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("ptap")
        assert driver_logueado.find_element(By.ID, "tabla-ptap").is_displayed()

    def test_busqueda_filtra_filas(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")
        filas_antes = len(page.obtener_filas_visibles("efluentes"))
        page.buscar("PTAAM")
        filas_despues = len(page.obtener_filas_visibles("efluentes"))
        assert filas_despues <= filas_antes
        page.limpiar_filtros()


# ════════════════════════════════════════════════════════
#  MODALES
# ════════════════════════════════════════════════════════

@pytest.mark.aguas
class TestMonitoreoModal:

    def test_modal_efluentes_abre_y_cierra(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_efluentes()
        assert page.modal_efluentes_abierto()
        page.cancelar_efluente()
        assert not page.modal_efluentes_abierto()

    def test_modal_ptard_abre_y_cierra(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_ptard()
        assert _modal_abierto(driver_logueado, "modal-ptard")
        page.cerrar_modal_ptard()

    def test_modal_ptap_abre_y_cierra(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_ptap()
        assert _modal_abierto(driver_logueado, "modal-ptap")
        page.cerrar_modal_ptap()


# ════════════════════════════════════════════════════════
#  CRUD EFLUENTES
# ════════════════════════════════════════════════════════

@pytest.mark.aguas
class TestEfluentesCRUD:

    def test_crear_registro_efluente(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")
        filas_antes = len(page.obtener_filas_visibles("efluentes"))
        page.abrir_modal_efluentes()
        form = driver_logueado.find_element(By.ID, "form-efluentes")
        driver_logueado.execute_script(
            "arguments[0].value = '2026-03-31';",
            form.find_element(By.NAME, "fecha")
        )
        Select(form.find_element(By.NAME, "efluente")).select_by_index(1)
        Select(form.find_element(By.NAME, "supervisor")).select_by_index(1)
        for nombre, valor in [
            ("caudal_max","60.000"),("caudal_tratado","18.000"),("tss","5.225"),
            ("cu_tot","0.363"),("pb_tot","0.001"),("zn_tot","1.524"),("fe_tot","121.500"),
            ("as_tot","0.001"),("ph_lab","7.20"),("tss_lmp","25.000"),("cu_lmp","0.400"),
            ("pb_lmp","0.200"),("zn_lmp","1.500"),("fe_lmp","1.600"),("as_lmp","0.100"),
            ("cn_lmp","1.000"),("cr_vi_lmp","0.100"),("ph_min","6.00"),("ph_max","9.00"),
        ]:
            c = form.find_element(By.NAME, nombre)
            driver_logueado.execute_script("arguments[0].value = '';", c)
            c.send_keys(valor)
        driver_logueado.execute_script(
            "arguments[0].click();",
            form.find_element(By.CSS_SELECTOR, ".btn-primary")
        )
        time.sleep(2)
        page.ir()
        page.cambiar_tipo("efluentes")
        assert len(page.obtener_filas_visibles("efluentes")) > filas_antes

    def test_editar_registro_efluente(self, driver_logueado):
        """Editar el primer registro de efluente — abre el modal en modo edición."""
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")

        filas = page.obtener_filas_visibles("efluentes")
        if not filas:
            pytest.skip("No hay registros de efluentes para editar")

        # Click en el botón de editar de la primera fila
        btn_editar = filas[0].find_element(By.CSS_SELECTOR, ".btn-icon-edit")
        driver_logueado.execute_script("arguments[0].click();", btn_editar)
        
        # Esperar a que el modal se abra (puede tardar por el fetch)
        try:
            WebDriverWait(driver_logueado, 5).until(
                lambda d: _modal_abierto(d, "modal-efluentes")
            )
            modal_abierto = True
        except:
            modal_abierto = False

        assert modal_abierto, "No se abrió ningún modal al hacer click en editar"

        # Cerrar el modal
        page.cancelar_efluente()
        time.sleep(0.3)

    def test_eliminar_registro_efluente(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")
        filas_antes = page.obtener_filas_visibles("efluentes")
        if not filas_antes:
            pytest.skip("No hay registros para eliminar")
        driver_logueado.execute_script(
            "arguments[0].click();",
            filas_antes[0].find_element(
                By.CSS_SELECTOR, ".btn-red, .btn-icon-danger, [onclick*='eliminar']"
            )
        )
        time.sleep(0.5)
        try:
            driver_logueado.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(1.5)
        page.ir()
        page.cambiar_tipo("efluentes")
        assert len(page.obtener_filas_visibles("efluentes")) < len(filas_antes)


# ════════════════════════════════════════════════════════
#  REPORTE ANA — smoke
# ════════════════════════════════════════════════════════

@pytest.mark.aguas
@pytest.mark.smoke
class TestReporteANA:

    def test_tabla_ana_carga(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        assert len(page.obtener_filas()) > 0

    def test_tabla_ana_columnas_correctas(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        textos = page.obtener_headers()
        assert any("FECHA"   in t for t in textos)
        assert any("CONT"    in t for t in textos)
        assert any("VOLUMEN" in t for t in textos)
        assert any("CAUDAL"  in t for t in textos)

    def test_modal_ana_se_abre(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal()
        assert page.modal_abierto()

    def test_modal_ana_cancelar(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal()
        page.cancelar()
        assert not page.modal_abierto()

    def test_calculo_automatico_volumen_y_caudal(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal()
        page.llenar_reporte("04/01/2026", 14600.00, 14608.92)
        volumen = page.obtener_volumen_calculado()
        caudal  = page.obtener_caudal_calculado()
        assert volumen != "" and caudal != ""
        assert float(volumen) == pytest.approx(8.92, abs=0.01)
        page.cancelar()

    def test_filtro_fecha_ana(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.filtrar_fechas("2021-05-01", "2021-05-03")
        time.sleep(0.5)
        filas_despues = len([tr for tr in page.obtener_filas() if tr.is_displayed()])
        assert filas_despues <= filas_antes
        page.limpiar_filtros()


# ════════════════════════════════════════════════════════
#  REPORTE ANA — CRUD
# ════════════════════════════════════════════════════════

@pytest.mark.aguas
class TestReporteANACRUD:

    def test_crear_reporte_ana(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.abrir_modal()
        driver_logueado.execute_script(
            "document.getElementById('ana_fecha').value = '2026-03-31';"
        )
        page.llenar_reporte(None, 14620.00, 14628.92)
        btn = driver_logueado.find_element(*ReporteANAPage.BTN_GUARDAR)
        driver_logueado.execute_script("arguments[0].scrollIntoView(true);", btn)
        driver_logueado.execute_script("arguments[0].click();", btn)
        WebDriverWait(driver_logueado, 15).until(
            lambda d: d.find_element(By.ID, "anaEstado").text.strip() != ""
            and "Guardando" not in d.find_element(By.ID, "anaEstado").text
        )
        estado = driver_logueado.find_element(By.ID, "anaEstado").text
        assert "error" not in estado.lower(), f"Error: {estado}"
        time.sleep(2)
        page.ir()
        assert len(page.obtener_filas()) > filas_antes

    def test_editar_reporte_ana(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay reportes ANA para editar")
        driver_logueado.execute_script(
            "arguments[0].click();",
            filas[0].find_element(By.CSS_SELECTOR, ".btn-icon-edit")
        )
        _esperar_modal(driver_logueado, "modalANA")
        assert _modal_abierto(driver_logueado, "modalANA")
        assert driver_logueado.find_element(By.ID, "ana_cont_ini").get_attribute("value") != ""
        page.cancelar()

    def test_eliminar_reporte_ana(self, driver_logueado):
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay reportes para eliminar")
        driver_logueado.execute_script(
            "arguments[0].click();",
            filas_antes[0].find_element(
                By.CSS_SELECTOR, ".btn-red, .btn-icon-danger, [onclick*='eliminar']"
            )
        )
        time.sleep(0.5)
        try:
            driver_logueado.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(1.5)
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)