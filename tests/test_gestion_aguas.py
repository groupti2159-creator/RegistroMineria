# ════════════════════════════════════════════════════════
#  ecoSupervisor — tests/test_gestion_aguas.py
#  Pruebas Selenium: Monitoreo + ANA — flujos completos
# ════════════════════════════════════════════════════════

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.aguas_page import MonitoreoPage, ReporteANAPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  SMOKE — Tablas y navegación
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
#  MODALES — abrir y cancelar
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
        driver_logueado.find_element(*MonitoreoPage.BTN_NUEVO_PTARD).click()
        wait  = WebDriverWait(driver_logueado, 8)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "modal-ptard")))
        assert modal.is_displayed()
        driver_logueado.find_element(By.CSS_SELECTOR, "#modal-ptard .btn-secondary").click()
        time.sleep(0.3)

    def test_modal_ptap_abre_y_cierra(self, driver_logueado):
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        driver_logueado.find_element(*MonitoreoPage.BTN_NUEVO_PTAP).click()
        wait  = WebDriverWait(driver_logueado, 8)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "modal-ptap")))
        assert modal.is_displayed()
        driver_logueado.find_element(By.CSS_SELECTOR, "#modal-ptap .btn-secondary").click()
        time.sleep(0.3)


# ════════════════════════════════════════════════════════
#  CRUD EFLUENTES — crear, editar, eliminar
# ════════════════════════════════════════════════════════

@pytest.mark.aguas
class TestEfluentesCRUD:

    def test_crear_registro_efluente(self, driver_logueado):
        """Crear un nuevo registro de efluente y verificar que aparece en tabla."""
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")
        filas_antes = len(page.obtener_filas_visibles("efluentes"))

        page.abrir_modal_efluentes()

        form = driver_logueado.find_element(By.ID, "form-efluentes")

        # Fecha
        driver_logueado.execute_script(
            "arguments[0].value = '2026-03-31';",
            form.find_element(By.NAME, "fecha")
        )
        # Efluente
        Select(form.find_element(By.NAME, "efluente")).select_by_index(1)
        # Supervisor
        Select(form.find_element(By.NAME, "supervisor")).select_by_index(1)
        # Parámetros
        for nombre, valor in [
            ("caudal_max", "60.000"),
            ("caudal_tratado", "18.000"),
            ("tss", "5.225"),
            ("cu_tot", "0.363"),
            ("pb_tot", "0.001"),
            ("zn_tot", "1.524"),
            ("fe_tot", "121.500"),
            ("as_tot", "0.001"),
            ("ph_lab", "7.20"),
            ("tss_lmp", "25.000"),
            ("cu_lmp", "0.400"),
            ("pb_lmp", "0.200"),
            ("zn_lmp", "1.500"),
            ("fe_lmp", "1.600"),
            ("as_lmp", "0.100"),
            ("cn_lmp", "1.000"),
            ("cr_vi_lmp", "0.100"),
            ("ph_min", "6.00"),
            ("ph_max", "9.00"),
        ]:
            campo = form.find_element(By.NAME, nombre)
            driver_logueado.execute_script("arguments[0].value = '';", campo)
            campo.send_keys(valor)

        # Guardar
        form.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        time.sleep(2)

        # Verificar que hay una fila más
        page.ir()
        page.cambiar_tipo("efluentes")
        filas_despues = len(page.obtener_filas_visibles("efluentes"))
        assert filas_despues > filas_antes, \
            f"No se creó el registro. Antes: {filas_antes}, Después: {filas_despues}"

    def test_editar_registro_efluente(self, driver_logueado):
        """Editar el primer registro de efluente."""
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")

        filas = page.obtener_filas_visibles("efluentes")
        if not filas:
            pytest.skip("No hay registros de efluentes para editar")

        # Click en editar de la primera fila
        btn_editar = filas[0].find_element(By.CSS_SELECTOR, ".btn-icon-edit")
        btn_editar.click()

        wait  = WebDriverWait(driver_logueado, 8)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "modal-efluentes")))
        assert modal.is_displayed(), "El modal de editar no se abrió"

        # Verificar que el título cambió a Editar
        titulo = driver_logueado.find_element(By.CSS_SELECTOR, "#modal-efluentes .modal-title")
        assert "Editar" in titulo.text or "editar" in titulo.text.lower()

        # Cancelar
        driver_logueado.find_element(By.CSS_SELECTOR, "#modal-efluentes .btn-secondary").click()
        time.sleep(0.3)

    def test_eliminar_registro_efluente(self, driver_logueado):
        """Eliminar el primer registro de efluente más reciente."""
        page = MonitoreoPage(driver_logueado, BASE_URL)
        page.ir()
        page.cambiar_tipo("efluentes")

        filas_antes = page.obtener_filas_visibles("efluentes")
        if not filas_antes:
            pytest.skip("No hay registros para eliminar")

        # Click en eliminar de la primera fila
        btn_eliminar = filas_antes[0].find_element(By.CSS_SELECTOR, ".btn-red, .btn-icon-danger")
        btn_eliminar.click()

        # Confirmar el alert
        time.sleep(0.5)
        try:
            alert = driver_logueado.switch_to.alert
            alert.accept()
        except Exception:
            pass  # confirm() puede manejarse diferente

        time.sleep(1.5)
        page.ir()
        page.cambiar_tipo("efluentes")
        filas_despues = page.obtener_filas_visibles("efluentes")
        assert len(filas_despues) < len(filas_antes), \
            "El registro no se eliminó"


# ════════════════════════════════════════════════════════
#  REPORTE ANA — smoke + CRUD completo
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
        assert any("FECHA"   in t for t in textos), f"Falta FECHA. Headers: {textos}"
        assert any("CONT"    in t for t in textos), f"Falta CONT. Headers: {textos}"
        assert any("VOLUMEN" in t for t in textos), f"Falta VOLUMEN. Headers: {textos}"
        assert any("CAUDAL"  in t for t in textos), f"Falta CAUDAL. Headers: {textos}"

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
        """Volumen y caudal se calculan automáticamente al ingresar contómetros."""
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal()

        cont_ini = 14600.00
        cont_fin = 14608.92
        page.llenar_reporte("04/01/2026", cont_ini, cont_fin)

        volumen = page.obtener_volumen_calculado()
        caudal  = page.obtener_caudal_calculado()

        assert volumen != "", "El volumen no se calculó"
        assert caudal  != "", "El caudal no se calculó"
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


@pytest.mark.aguas
class TestReporteANACRUD:

    def test_crear_reporte_ana(self, driver_logueado):
        """Crear un nuevo reporte ANA y verificar que aparece en tabla."""
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())

        page.abrir_modal()
        page.llenar_reporte("03/31/2026", 14620.00, 14628.92)
        page.guardar()

        estado = page.estado_texto()
        assert "Guardado" in estado or "✅" in estado, \
            f"Estado inesperado: {estado}"

        time.sleep(2)
        page.ir()
        filas_despues = len(page.obtener_filas())
        assert filas_despues > filas_antes, \
            f"El reporte no se creó. Antes: {filas_antes}, Después: {filas_despues}"

    def test_editar_reporte_ana(self, driver_logueado):
        """Editar el primer reporte ANA."""
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()

        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay reportes ANA para editar")

        btn_editar = filas[0].find_element(By.CSS_SELECTOR, ".btn-icon-edit")
        btn_editar.click()

        wait  = WebDriverWait(driver_logueado, 8)
        modal = wait.until(
            lambda d: d.find_element(By.ID, "modalANA").get_attribute("style") != "display:none;"
        )
        time.sleep(0.3)

        titulo = driver_logueado.find_element(By.ID, "modalANA-titulo")
        assert "Editar" in titulo.text, \
            f"El modal no dice Editar: {titulo.text}"

        page.cancelar()

    def test_eliminar_reporte_ana(self, driver_logueado):
        """Eliminar el primer reporte ANA."""
        page = ReporteANAPage(driver_logueado, BASE_URL)
        page.ir()

        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay reportes para eliminar")

        btn_eliminar = filas_antes[0].find_element(By.CSS_SELECTOR, ".btn-red, .btn-icon-danger")
        btn_eliminar.click()

        time.sleep(0.5)
        try:
            alert = driver_logueado.switch_to.alert
            alert.accept()
        except Exception:
            pass

        time.sleep(1.5)
        page.ir()
        filas_despues = page.obtener_filas()
        assert len(filas_despues) < len(filas_antes), \
            "El reporte no se eliminó"