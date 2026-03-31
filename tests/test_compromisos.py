# ════════════════════════════════════════════════════════
#  ecoSupervisor — tests/test_compromisos.py
#  Pruebas Selenium: módulo Compromisos — flujos completos
# ════════════════════════════════════════════════════════

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from tests.pages.compromisos_page import CompromisosPage

BASE_URL = "http://127.0.0.1:8080"


# ── Helpers ──────────────────────────────────────────────
def crear_archivo_prueba(nombre="evidencia_test.pdf"):
    """Crea un archivo PDF mínimo válido para pruebas de upload."""
    ruta = os.path.join(os.path.dirname(__file__), nombre)
    with open(ruta, "wb") as f:
        # PDF mínimo válido
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj "
                b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj "
                b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj\n"
                b"xref\n0 4\n0000000000 65535 f\n"
                b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF")
    return ruta


# ════════════════════════════════════════════════════════
#  SMOKE — Tabla y navegación básica
# ════════════════════════════════════════════════════════

@pytest.mark.compromisos
@pytest.mark.smoke
class TestCompromisosTabla:

    def test_tabla_carga_correctamente(self, driver_logueado):
        """La tabla carga y muestra exactamente 10 registros fijos."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.obtener_total_registros() == 10

    def test_cambiar_periodo_mantiene_tabla(self, driver_logueado):
        """Cambiar mes/año recarga sin error."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(1, 2026)
        assert len(page.obtener_filas()) > 0

    def test_chips_entidad_visibles(self, driver_logueado):
        """Los chips de entidad regulatoria se muestran."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        chips = driver_logueado.find_elements(By.CSS_SELECTOR, ".entidad-chip")
        assert len(chips) > 0

    def test_exportar_disponible(self, driver_logueado):
        """El botón Exportar .xlsx tiene href correcto."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        btn  = driver_logueado.find_element(*CompromisosPage.BTN_EXPORTAR)
        href = btn.get_attribute("href")
        assert "exportar" in href and "mes=" in href


# ════════════════════════════════════════════════════════
#  MODAL EDITAR — abrir, campos, supervisor, observaciones
# ════════════════════════════════════════════════════════

@pytest.mark.compromisos
class TestCompromisosModalEditar:

    def test_modal_se_abre(self, driver_logueado):
        """El modal de editar se abre al hacer click en ✏️."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)
        assert page.modal_esta_abierto()
        page.cancelar_modal()

    def test_modal_muestra_datos_readonly(self, driver_logueado):
        """El modal pre-carga nombre y entidad como campos read-only."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)

        assert page.obtener_nombre_en_modal()  != ""
        assert page.obtener_entidad_en_modal() != ""
        page.cancelar_modal()

    def test_modal_cancelar_cierra(self, driver_logueado):
        """El botón Cancelar cierra el modal."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)
        page.cancelar_modal()
        assert not page.modal_esta_abierto()

    def test_modal_cierra_click_fuera(self, driver_logueado):
        """Click fuera del modal lo cierra."""
        from selenium.webdriver.common.action_chains import ActionChains

        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_editar(0)

        overlay = driver_logueado.find_element(*CompromisosPage.MODAL_EDITAR)
        ActionChains(driver_logueado).move_to_element_with_offset(overlay, 5, 5).click().perform()
        time.sleep(0.4)
        assert not page.modal_esta_abierto()

    def test_guardar_observaciones(self, driver_logueado):
        """Se pueden editar y guardar observaciones desde el modal."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)

        obs_nueva = f"Test Selenium {int(time.time())}"
        page.escribir_observaciones(obs_nueva)
        page.guardar_modal()

        estado = page.estado_guardado_texto()
        assert "Guardado" in estado or "✅" in estado

        time.sleep(1.5)
        # Verificar que la observación aparece en la tabla
        page.ir_con_periodo(3, 2026)
        filas = page.obtener_filas()
        textos_filas = " ".join([f.text for f in filas])
        assert obs_nueva in textos_filas, "La observación no se guardó en la tabla"

    def test_guardar_supervisor(self, driver_logueado):
        """Se puede seleccionar y guardar un supervisor desde el modal."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)

        # Seleccionar el primer supervisor disponible
        sel = driver_logueado.find_element(*CompromisosPage.SEL_SUPERVISOR)
        opciones = sel.find_elements(By.TAG_NAME, "option")
        supervisor_elegido = None
        for op in opciones:
            if op.get_attribute("value"):
                op.click()
                supervisor_elegido = op.text
                break

        if supervisor_elegido:
            page.guardar_modal()
            estado = page.estado_guardado_texto()
            assert "Guardado" in estado or "✅" in estado

    def test_modal_muestra_banner_evidencia(self, driver_logueado):
        """El modal muestra el banner correcto según si hay evidencia."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)

        con = driver_logueado.find_element(*CompromisosPage.DIV_CON_EVIDENCIA)
        sin = driver_logueado.find_element(*CompromisosPage.DIV_SIN_EVIDENCIA)
        assert con.is_displayed() or sin.is_displayed()
        page.cancelar_modal()


# ════════════════════════════════════════════════════════
#  EVIDENCIA — subir archivo, ver, versiones
# ════════════════════════════════════════════════════════

@pytest.mark.compromisos
class TestCompromisosEvidencia:

    def test_subir_evidencia_desde_modal(self, driver_logueado):
        """Se puede subir un archivo PDF como evidencia desde el modal."""
        ruta = crear_archivo_prueba("evidencia_test.pdf")

        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)
        page.abrir_modal_editar(0)

        # Subir archivo
        input_file = driver_logueado.find_element(By.ID, "editComp_archivo")
        input_file.send_keys(ruta)
        time.sleep(0.5)

        # Verificar que se muestra el nombre del archivo
        label = driver_logueado.find_element(By.ID, "editComp_archivoLabel")
        assert "evidencia_test.pdf" in label.text

        # Guardar
        page.guardar_modal()
        estado = page.estado_guardado_texto()
        assert "Guardado" in estado or "✅" in estado

        time.sleep(1.5)

        # Verificar que ahora aparece el ícono verde en la tabla
        page.ir_con_periodo(3, 2026)
        assert page.tiene_evidencia_fila(0), \
            "Después de subir, la fila debe mostrar ícono de evidencia"

        # Limpiar archivo temporal
        if os.path.exists(ruta):
            os.remove(ruta)

    def test_ver_evidencia_una_version(self, driver_logueado):
        """Click en ojo abre nueva pestaña si hay 1 sola versión."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia — ejecuta test_subir primero")

        ventanas_antes = len(driver_logueado.window_handles)
        page.click_ver_evidencia(0)
        time.sleep(1.5)

        popover_visible  = page.popover_visible()
        nueva_pestana    = len(driver_logueado.window_handles) > ventanas_antes

        assert popover_visible or nueva_pestana, \
            "Click en ojo no abrió popover ni nueva pestaña"

        if nueva_pestana:
            driver_logueado.switch_to.window(driver_logueado.window_handles[-1])
            driver_logueado.close()
            driver_logueado.switch_to.window(driver_logueado.window_handles[0])

    def test_popover_versiones_muestra_lista(self, driver_logueado):
        """Si hay múltiples versiones, el popover las lista con botones ver/bajar."""
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
                assert len(btns) == 2, "Cada versión debe tener botón Ver y Descargar"

            # Cerrar popover
            driver_logueado.find_element(
                By.CSS_SELECTOR, ".versiones-popover__close"
            ).click()
        else:
            # Solo 1 versión — se abrió nueva pestaña, cerrarla
            if len(driver_logueado.window_handles) > 1:
                driver_logueado.switch_to.window(driver_logueado.window_handles[-1])
                driver_logueado.close()
                driver_logueado.switch_to.window(driver_logueado.window_handles[0])

    def test_popover_cierra_click_fuera(self, driver_logueado):
        """El popover se cierra al hacer click fuera."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia")

        page.click_ver_evidencia(0)
        time.sleep(0.5)

        if page.popover_visible():
            # Click en el body fuera del popover
            driver_logueado.find_element(By.CSS_SELECTOR, "h2.section-title").click()
            time.sleep(0.4)
            assert not page.popover_visible(), "El popover no se cerró al click fuera"

    def test_modal_tiene_botones_ver_y_bajar(self, driver_logueado):
        """El modal muestra botones Ver y Bajar si hay evidencia."""
        page = CompromisosPage(driver_logueado, BASE_URL)
        page.ir_con_periodo(3, 2026)

        if not page.tiene_evidencia_fila(0):
            pytest.skip("Fila 0 no tiene evidencia")

        page.abrir_modal_editar(0)

        assert page.modal_tiene_evidencia(), \
            "El modal debe mostrar el banner verde de evidencia"

        btn_ver    = driver_logueado.find_element(By.ID, "editComp_btnVer")
        btn_bajar  = driver_logueado.find_element(By.ID, "editComp_btnDescargar")

        assert btn_ver.is_displayed(),   "Falta botón Ver en el modal"
        assert btn_bajar.is_displayed(), "Falta botón Bajar en el modal"

        href_ver = btn_ver.get_attribute("href")
        assert "ver-evidencia" in href_ver or "ver-version" in href_ver

        page.cancelar_modal()