import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.residuos_page import GeneracionPage, SubpaginaResiduosPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  GENERACIÓN DIARIA — Smoke
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
@pytest.mark.smoke
class TestGeneracionSmoke:

    def test_pagina_carga(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert "/residuos/generacion" in driver_logueado.current_url

    def test_tabla_visible(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.TABLA).is_displayed()

    def test_boton_nuevo_visible(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.BTN_NUEVO).is_displayed()

    def test_tabla_columna_fecha(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        headers = [h.text.upper() for h in
                   driver_logueado.find_elements(By.CSS_SELECTOR, ".gen-table thead th")]
        assert any("FECHA" in t for t in headers)

    def test_tabla_columna_generacion(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        headers = [h.text.upper() for h in
                   driver_logueado.find_elements(By.CSS_SELECTOR, ".gen-table thead th")]
        assert any("GEN" in t or "DIARIA" in t for t in headers)

    def test_boton_exportar_visible(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.BTN_EXPORTAR).is_displayed()


# ════════════════════════════════════════════════════════
#  GENERACIÓN DIARIA — Modal nuevo registro
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
class TestGeneracionModalNuevo:

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
        campos = driver_logueado.find_elements(By.CSS_SELECTOR, "#modal-overlay input[type='date']")
        assert len(campos) > 0
        page.cerrar_modal()

    def test_modal_tiene_campos_numericos(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_nuevo()
        campos = driver_logueado.find_elements(
            By.CSS_SELECTOR, "#modal-overlay input[type='number'], #modal-overlay input[type='text']"
        )
        assert len(campos) > 0
        page.cerrar_modal()

    def test_modal_cierra(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_nuevo()
        page.cerrar_modal()
        time.sleep(0.5)
        assert not page.modal_abierto()


# ════════════════════════════════════════════════════════
#  GENERACIÓN DIARIA — Filtros de fecha
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
class TestGeneracionFiltros:

    def test_filtro_desde_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.FILTRO_DESDE).is_displayed()

    def test_filtro_hasta_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.FILTRO_HASTA).is_displayed()

    def test_boton_filtrar_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.BTN_FILTRAR).is_displayed()

    def test_boton_limpiar_presente(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*GeneracionPage.BTN_LIMPIAR).is_displayed()

    def test_filtrar_por_rango_de_fechas(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.filtrar_fechas("2025-01-01", "2025-06-30")
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes
        page.limpiar_filtros()

    def test_limpiar_restaura_resultados(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas_total = len(page.obtener_filas())
        page.filtrar_fechas("2025-01-01", "2025-01-01")
        page.limpiar_filtros()
        assert len(page.obtener_filas()) >= filas_total


# ════════════════════════════════════════════════════════
#  GENERACIÓN DIARIA — Acciones en filas
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
class TestGeneracionAccionesFila:

    def test_filas_tienen_boton_ver(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        assert filas[0].find_element(By.CSS_SELECTOR, ".btn-ver").is_displayed()

    def test_filas_tienen_boton_editar(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        assert filas[0].find_element(By.CSS_SELECTOR, ".btn-edit").is_displayed()

    def test_ver_detalle_abre_modal(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.ver_detalle_fila(0)
        assert page.modal_detalle_abierto()
        page.cerrar_modal_detalle()

    def test_editar_abre_modal_con_datos(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros")
        page.editar_fila(0)
        assert page.modal_abierto()
        campos_fecha = driver_logueado.find_elements(
            By.CSS_SELECTOR, "#modal-overlay input[type='date']"
        )
        if campos_fecha:
            assert campos_fecha[0].get_attribute("value") != ""
        page.cerrar_modal()

    def test_eliminar_reduce_conteo(self, driver_logueado):
        page = GeneracionPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay registros para eliminar")
        page.eliminar_fila(0)
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)


# ════════════════════════════════════════════════════════
#  COMERCIALIZABLE
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
@pytest.mark.smoke
class TestComercializableSmoke:

    def test_pagina_carga(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        assert "/residuos/comercializable" in driver_logueado.current_url

    def test_tabla_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        assert page.tabla_visible()

    def test_boton_nuevo_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        assert page.btn_nuevo_visible()

    def test_boton_exportar_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        assert page.exportar_btn_visible()


@pytest.mark.residuos
class TestComercializableCRUD:

    def test_modal_nuevo_se_abre(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        page.abrir_modal_nuevo()
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_modal_nuevo_tiene_campo_fecha(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        page.abrir_modal_nuevo()
        campo = driver_logueado.find_element(By.ID, "com-fecha")
        assert campo.is_displayed()
        page.cerrar_modal()

    def test_modal_nuevo_tiene_campo_peso(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        page.abrir_modal_nuevo()
        campo = driver_logueado.find_element(By.ID, "com-peso")
        assert campo.is_displayed()
        page.cerrar_modal()

    def test_modal_nuevo_cierra(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        page.abrir_modal_nuevo()
        page.cerrar_modal()
        time.sleep(0.5)
        assert not page.modal_abierto()

    def test_filtro_fecha_funciona(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.filtrar_fechas("2025-01-01", "2025-06-30")
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes
        page.limpiar_filtros()

    def test_editar_primer_registro_abre_modal(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros comercializables")
        assert page.abrir_modal_editar(0)
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_editar_trae_campo_fecha_precargado(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros comercializables")
        page.abrir_modal_editar(0)
        valor = driver_logueado.find_element(By.ID, "com-fecha").get_attribute("value")
        assert valor != ""
        page.cerrar_modal()

    def test_eliminar_reduce_conteo(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "comercializable")
        page.ir()
        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay registros para eliminar")
        page.eliminar_fila(0)
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)


# ════════════════════════════════════════════════════════
#  COMPOSTAJE
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
@pytest.mark.smoke
class TestCompostajeSmoke:

    def test_pagina_carga(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        assert "/residuos/compostaje" in driver_logueado.current_url

    def test_tabla_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        assert page.tabla_visible()

    def test_boton_nuevo_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        assert page.btn_nuevo_visible()

    def test_boton_exportar_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        assert page.exportar_btn_visible()


@pytest.mark.residuos
class TestCompostajeCRUD:

    def test_modal_nuevo_se_abre(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        page.abrir_modal_nuevo()
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_modal_tiene_campo_fecha(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        page.abrir_modal_nuevo()
        assert driver_logueado.find_element(By.ID, "comp-fecha").is_displayed()
        page.cerrar_modal()

    def test_modal_tiene_campo_volumen(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        page.abrir_modal_nuevo()
        assert driver_logueado.find_element(By.ID, "comp-volumen").is_displayed()
        page.cerrar_modal()

    def test_modal_cierra(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        page.abrir_modal_nuevo()
        page.cerrar_modal()
        time.sleep(0.5)
        assert not page.modal_abierto()

    def test_filtro_fecha_funciona(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.filtrar_fechas("2025-01-01", "2025-06-30")
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes
        page.limpiar_filtros()

    def test_editar_primer_registro_abre_modal(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros de compostaje")
        assert page.abrir_modal_editar(0)
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_eliminar_reduce_conteo(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "compostaje")
        page.ir()
        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay registros de compostaje para eliminar")
        page.eliminar_fila(0)
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)


# ════════════════════════════════════════════════════════
#  MATPEL
# ════════════════════════════════════════════════════════

@pytest.mark.residuos
@pytest.mark.smoke
class TestMatpelSmoke:

    def test_pagina_carga(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        assert "/residuos/matpel" in driver_logueado.current_url

    def test_tabla_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        assert page.tabla_visible()

    def test_boton_nuevo_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        assert page.btn_nuevo_visible()

    def test_boton_exportar_visible(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        assert page.exportar_btn_visible()


@pytest.mark.residuos
class TestMatpelCRUD:

    def test_modal_nuevo_se_abre(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        page.abrir_modal_nuevo()
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_modal_tiene_campo_fecha(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        page.abrir_modal_nuevo()
        assert driver_logueado.find_element(By.ID, "mat-fecha").is_displayed()
        page.cerrar_modal()

    def test_modal_tiene_campo_peso(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        page.abrir_modal_nuevo()
        assert driver_logueado.find_element(By.ID, "mat-peso").is_displayed()
        page.cerrar_modal()

    def test_modal_cierra(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        page.abrir_modal_nuevo()
        page.cerrar_modal()
        time.sleep(0.5)
        assert not page.modal_abierto()

    def test_filtro_fecha_funciona(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.filtrar_fechas("2025-01-01", "2025-06-30")
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes
        page.limpiar_filtros()

    def test_editar_primer_registro_abre_modal(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay registros de matpel")
        assert page.abrir_modal_editar(0)
        assert page.modal_abierto()
        page.cerrar_modal()

    def test_eliminar_reduce_conteo(self, driver_logueado):
        page = SubpaginaResiduosPage(driver_logueado, BASE_URL, "matpel")
        page.ir()
        filas_antes = page.obtener_filas()
        if not filas_antes:
            pytest.skip("No hay registros de matpel para eliminar")
        page.eliminar_fila(0)
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)
