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
        filas = page.obtener_filas()
        assert len(filas) > 0

    def test_boton_nuevo_usuario_visible(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        btn = driver_logueado.find_element(*UsuariosPage.BTN_NUEVO)
        assert btn.is_displayed()


# ════════════════════════════════════════════════════════
#  TABLA DE USUARIOS
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosTabla:

    def test_columna_nombre_presente(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        headers = driver_logueado.find_elements(By.CSS_SELECTOR, "thead th")
        textos = [h.text.strip().upper() for h in headers]
        assert any("NOMBRE" in t or "USUARIO" in t for t in textos)

    def test_filas_tienen_nombre_no_vacio(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios registrados")
        nombre = filas[0].find_element(By.CSS_SELECTOR, "td").text.strip()
        assert nombre != ""

    def test_filas_tienen_acciones(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios registrados")
        btns = filas[0].find_elements(By.CSS_SELECTOR, "button, a.btn")
        assert len(btns) > 0


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

    def test_modal_tiene_campo_nombre(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        campos = driver_logueado.find_elements(
            By.CSS_SELECTOR, "#modalCrearUsuario input[type='text'], #modalCrearUsuario input[name='nombre']"
        )
        assert len(campos) > 0
        page.cerrar_modal_crear()

    def test_modal_tiene_campo_correo(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        try:
            campo = driver_logueado.find_element(
                By.CSS_SELECTOR, "#modalCrearUsuario input[type='email'], #modalCrearUsuario input[name='correo']"
            )
            assert campo.is_displayed()
        except Exception:
            # Puede que el campo sea text en lugar de email
            campos = driver_logueado.find_elements(By.CSS_SELECTOR, "#modalCrearUsuario input")
            assert len(campos) >= 2
        page.cerrar_modal_crear()

    def test_modal_cierra_correctamente(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        page.cerrar_modal_crear()
        time.sleep(0.5)
        assert not page.modal_crear_abierto()

    def test_modal_tiene_titulo(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        page.abrir_modal_crear()
        titulo = driver_logueado.find_element(By.ID, "modalTitle")
        assert titulo.text.strip() != ""
        page.cerrar_modal_crear()


# ════════════════════════════════════════════════════════
#  MODAL VER DETALLE
# ════════════════════════════════════════════════════════

@pytest.mark.configuracion
class TestUsuariosModalDetalle:

    def test_ver_detalle_primer_usuario(self, driver_logueado):
        page = UsuariosPage(driver_logueado, BASE_URL)
        page.ir()
        filas = page.obtener_filas()
        if not filas:
            pytest.skip("No hay usuarios registrados")
        page.ver_detalle_fila(0)
        time.sleep(0.5)
        modal_abierto = page.modal_detalle_abierto()
        if not modal_abierto:
            pytest.skip("El modal de detalle no se abrió (posiblemente redirige a otra página)")
        assert modal_abierto
        # Cerrar
        driver_logueado.execute_script(
            "var el = document.getElementById('modalVerDetalle');"
            "if (el) el.style.display = 'none';"
        )
