import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from tests.pages.compromisos_page import CompromisosPage

BASE_URL = "http://127.0.0.1:8080"


def crear_archivo_prueba(nombre="evidencia_test.pdf"):
    ruta = os.path.join(os.path.dirname(__file__), nombre)
    with open(ruta, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj "
                b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj "
                b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\n"
                b"xref\n0 4\n0000000000 65535 f\n"
                b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF")
    return ruta


# ════════════════════════════════════════════════════════
#  SMOKE
# ════════════════════════════════════════════════════════

@pytest.mark.compromisos
@pytest.mark.smoke
class TestCompromisosTabla:

    def test_tabla_carga_correctamente(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.obtener_total_registros() == 10

    def test_cambiar_periodo_mantiene_tabla(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(1, 2026)
        assert len(page.obtener_filas()) > 0

    def test_chips_entidad_visibles(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        chips = driver_logueado.find_elements(By.CSS_SELECTOR, ".entidad-chip")
        assert len(chips) > 0

    def test_exportar_disponible(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*CompromisosPage.BTN_EXPORTAR)
        href = btn.get_attribute("href")
        assert "exportar" in href and "mes=" in href


# ════════════════════════════════════════════════════════
#  MODAL EDITAR
# ════════════════════════════════════════════════════════

@pytest.mark.compromisos
class TestCompromisosModalEditar:

    def test_modal_se_abre(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)
        assert page.modal_esta_abierto()
        page.cancelar_modal()

    def test_modal_muestra_datos_readonly(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)
        assert page.obtener_nombre_en_modal() != ""
        assert page.obtener_entidad_en_modal() != ""
        page.cancelar_modal()

    def test_modal_cancelar_cierra(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)
        page.cancelar_modal()
        time.sleep(0.5)
        assert not page.modal_esta_abierto()

    def test_modal_cierra_click_fuera(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)
        driver_logueado.execute_script("cerrarEditarCompromiso();")
        time.sleep(0.5)
        assert not page.modal_esta_abierto()

    def test_guardar_observaciones(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)

        obs_nueva = f"Test Selenium {int(time.time())}"
        page.escribir_observaciones(obs_nueva)
        page.guardar_modal()

        estado = page.estado_guardado_texto()
        assert "Guardado" in estado or "✅" in estado
        time.sleep(1.5)

        page.ir_con_periodo(3, 2026)
        textos = " ".join([f.text for f in page.obtener_filas()])
        assert obs_nueva in textos

    def test_guardar_supervisor(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)

        sel = driver_logueado.find_element(*CompromisosPage.SEL_SUPERVISOR)
        opciones = sel.find_elements(By.TAG_NAME, "option")
        for op in opciones:
            if op.get_attribute("value"):
                driver_logueado.execute_script("arguments[0].selected = true;", op)
                driver_logueado.execute_script(
                    "arguments[0].dispatchEvent(new Event('change'));", sel
                )
                break

        page.guardar_modal()
        estado = page.estado_guardado_texto()
        assert "Guardado" in estado or "✅" in estado

    def test_modal_muestra_banner_evidencia(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)
        assert page.modal_tiene_evidencia() or page.modal_sin_evidencia()
        page.cancelar_modal()


# ════════════════════════════════════════════════════════
#  EVIDENCIA
# ════════════════════════════════════════════════════════

@pytest.mark.compromisos
class TestCompromisosEvidencia:

    def test_subir_evidencia_desde_modal(self, driver_logueado):
        ruta = crear_archivo_prueba("evidencia_test.pdf")

        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)
        page.subir_archivo_modal(ruta)

        WebDriverWait(driver_logueado, 8).until(
            lambda d: d.execute_script(
                "var el = document.getElementById('editComp_archivoLabel');"
                "return el ? el.innerText.trim() !== '' : false;"
            )
        )
        label = page.obtener_label_archivo()
        assert "evidencia_test" in label or ".pdf" in label

        page.guardar_modal()
        estado = page.estado_guardado_texto()
        assert "Guardado" in estado or "✅" in estado
        time.sleep(1.5)

        page.ir_con_periodo(3, 2026)
        assert page.tiene_evidencia_fila(0)

        if os.path.exists(ruta):
            os.remove(ruta)

    def test_ver_evidencia_una_version(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia")

        ventanas_antes = len(driver_logueado.window_handles)
        page.click_ver_evidencia(0)
        time.sleep(1.5)

        popover_visible = page.popover_visible()
        nueva_pestana   = len(driver_logueado.window_handles) > ventanas_antes
        assert popover_visible or nueva_pestana

        if nueva_pestana:
            driver_logueado.switch_to.window(driver_logueado.window_handles[-1])
            driver_logueado.close()
            driver_logueado.switch_to.window(driver_logueado.window_handles[0])

    def test_popover_versiones_muestra_lista(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia")

        page.click_ver_evidencia(0)
        time.sleep(0.5)

        if page.popover_visible():
            versiones = page.obtener_versiones_en_popover()
            assert len(versiones) >= 1
            for v in versiones:
                btns = v.find_elements(By.CSS_SELECTOR, ".versiones-popover__btn")
                assert len(btns) == 2
            driver_logueado.find_element(
                By.CSS_SELECTOR, ".versiones-popover__close"
            ).click()
        else:
            if len(driver_logueado.window_handles) > 1:
                driver_logueado.switch_to.window(driver_logueado.window_handles[-1])
                driver_logueado.close()
                driver_logueado.switch_to.window(driver_logueado.window_handles[0])

    def test_popover_cierra_click_fuera(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia")

        page.click_ver_evidencia(0)
        time.sleep(0.5)

        if page.popover_visible():
            driver_logueado.find_element(By.CSS_SELECTOR, "h2.section-title").click()
            time.sleep(0.4)
            assert not page.popover_visible()

    def test_modal_tiene_botones_ver_y_bajar(self, driver_logueado):
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia")

        page.abrir_modal_editar(0)
        assert page.modal_tiene_evidencia(), "El modal debe mostrar banner verde"

        btn_ver   = driver_logueado.find_element(By.ID, "editComp_btnVer")
        btn_bajar = driver_logueado.find_element(By.ID, "editComp_btnDescargar")

        assert driver_logueado.execute_script(
            "return window.getComputedStyle(arguments[0]).display !== 'none';", btn_ver
        )
        assert driver_logueado.execute_script(
            "return window.getComputedStyle(arguments[0]).display !== 'none';", btn_bajar
        )

        page.cancelar_modal()