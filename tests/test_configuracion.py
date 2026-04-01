import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.pages.configuracion_page import UsuariosPage, ConfigDashboardPage

BASE_URL = "http://127.0.0.1:8080"


# ════════════════════════════════════════════════════════
#  SMOKE
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
@pytest.mark.smoke
class TestConfiguracionSmoke:

    def test_dashboard_carga(self, driver_logueado):
        page = ConfigDashboardPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.carga_correctamente()

    def test_usuarios_carga(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        assert "/configuracion/usuarios" in driver_logueado.current_url

    def test_tabla_usuarios_visible(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        assert page.tabla_visible()

    def test_tabla_tiene_filas(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        assert len(page.obtener_filas()) > 0

    def test_boton_nuevo_usuario_visible(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*UsuariosPage.BTN_NUEVO).is_displayed()

    def test_barra_busqueda_visible(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        assert driver_logueado.find_element(*UsuariosPage.INPUT_BUSCAR).is_displayed()


# ════════════════════════════════════════════════════════
#  TABLA DE USUARIOS
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosTabla:

    def test_columna_nombre_presente(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        headers = [h.text.upper() for h in
                   driver_logueado.find_elements(By.CSS_SELECTOR, "thead th")]
        assert any("NOMBRE" in t or "USUARIO" in t for t in headers)

    def test_columna_correo_presente(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        headers = [h.text.upper() for h in
                   driver_logueado.find_elements(By.CSS_SELECTOR, "thead th")]
        assert any("CORREO" in t or "EMAIL" in t for t in headers)

    def test_columna_estado_presente(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        headers = [h.text.upper() for h in
                   driver_logueado.find_elements(By.CSS_SELECTOR, "thead th")]
        assert any("ESTADO" in t or "ACTIVO" in t for t in headers)

    def test_filas_tienen_nombre_no_vacio(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        texto = filas[0].find_elements(By.TAG_NAME, "td")[0].text.strip()
        assert texto != ""

    def test_filas_tienen_botones_accion(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        btns = filas[0].find_elements(By.CSS_SELECTOR, "button")
        assert len(btns) > 0


# ════════════════════════════════════════════════════════
#  BÚSQUEDA / FILTRO
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosBusqueda:

    def test_busqueda_filtra_filas_visibles(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        if filas_antes == 0:
            pytest.skip("No hay usuarios")
        # Buscar texto que no debería existir
        page.buscar("xxxxxnoexistexxx")
        time.sleep(0.5)
        filas_despues = len(page.obtener_filas())
        assert filas_despues <= filas_antes

    def test_busqueda_por_nombre_existente(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        # Obtener primer carácter del primer nombre
        nombre = filas[0].find_elements(By.TAG_NAME, "td")[0].text.strip()
        if not nombre:
            pytest.skip("Nombre vacío")
        page.buscar(nombre[:3])
        time.sleep(0.5)
        filas_filtradas = page.obtener_filas()
        assert len(filas_filtradas) > 0

    def test_limpiar_busqueda_restaura_resultados(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        total = len(page.obtener_filas())
        page.buscar("xxxxxnoexistexxx")
        time.sleep(0.3)
        page.limpiar_busqueda()
        time.sleep(0.3)
        assert len(page.obtener_filas()) >= total


# ════════════════════════════════════════════════════════
#  MODAL CREAR USUARIO
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosModalCrear:

    def test_modal_se_abre(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert page.modal_crear_abierto()
        page.cerrar_modal_crear()

    def test_modal_tiene_titulo_crear(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        titulo = page.modal_title_texto()
        assert titulo.strip() != ""
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_dni(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(*UsuariosPage.CAMPO_DNI).is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_nombre(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(*UsuariosPage.CAMPO_NOMBRE).is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_correo(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(*UsuariosPage.CAMPO_CORREO).is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_password(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        assert driver_logueado.find_element(*UsuariosPage.CAMPO_PASSWORD).is_displayed()
        page.cerrar_modal_crear()

    def test_modal_tiene_boton_guardar(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        btn = driver_logueado.find_element(*UsuariosPage.BTN_GUARDAR)
        assert btn.is_displayed()
        page.cerrar_modal_crear()

    def test_modal_cierra(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        page.cerrar_modal_crear()
        time.sleep(0.5)
        assert not page.modal_crear_abierto()

    def test_crear_usuario_nuevo(self, driver_logueado):
        import random
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = len(page.obtener_filas())
        page.abrir_modal_crear()
        dni_nuevo = str(random.randint(10000000, 99999999))
        page.llenar_form_crear(
            dni=dni_nuevo,
            nombre=f"Usuario Test {int(time.time())}",
            correo=f"test{int(time.time())}@test.com",
        )
        page.guardar_usuario()
        page.ir()
        assert len(page.obtener_filas()) > filas_antes


# ════════════════════════════════════════════════════════
#  MODAL EDITAR USUARIO
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosModalEditar:

    def test_modal_editar_se_abre(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_editar(0)
        assert page.modal_crear_abierto()
        page.cerrar_modal_crear()

    def test_modal_editar_titulo_indica_edicion(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_editar(0)
        assert page.modal_editar_titulo_correcto()
        page.cerrar_modal_crear()

    def test_modal_editar_trae_datos_precargados(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_editar(0)
        nombre = driver_logueado.find_element(*UsuariosPage.CAMPO_NOMBRE).get_attribute("value")
        assert nombre.strip() != ""
        page.cerrar_modal_crear()

    def test_modal_editar_cierra(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_editar(0)
        page.cerrar_modal_crear()
        time.sleep(0.5)
        assert not page.modal_crear_abierto()


# ════════════════════════════════════════════════════════
#  MODAL VER DETALLE
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosModalDetalle:

    def test_modal_detalle_se_abre(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_detalle(0)
        assert page.modal_detalle_abierto()
        page.cerrar_modal_detalle()

    def test_modal_detalle_muestra_informacion(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_detalle(0)
        contenido = driver_logueado.find_element(
            By.CSS_SELECTOR, "#modalVerDetalle .modal-body, #modalVerDetalle"
        ).text
        assert contenido.strip() != ""
        page.cerrar_modal_detalle()

    def test_modal_detalle_cierra(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        page.abrir_modal_detalle(0)
        page.cerrar_modal_detalle()
        time.sleep(0.5)
        assert not page.modal_detalle_abierto()


# ════════════════════════════════════════════════════════
#  ELIMINAR USUARIO
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosEliminar:

    def test_boton_eliminar_presente_en_filas(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios")
        btn = filas[0].find_element(
            By.CSS_SELECTOR, "button[onclick*='eliminarUsuarioFisico']"
        )
        assert btn.is_displayed()

    def test_eliminar_usuario_reduce_conteo(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas_antes = page.obtener_filas()
        if len(filas_antes) <= 1:
            pytest.skip("No hay suficientes usuarios para eliminar de forma segura")
        page.click_eliminar_fila(len(filas_antes) - 1)  # Eliminar el último
        page.ir()
        assert len(page.obtener_filas()) < len(filas_antes)
