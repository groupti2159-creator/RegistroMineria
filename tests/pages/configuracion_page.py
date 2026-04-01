from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def _modal_abierto(driver, modal_id):
    try:
        return driver.execute_script(
            "var el = document.getElementById(arguments[0]);"
            "if (!el) return false;"
            "var s = window.getComputedStyle(el);"
            "return s.display !== 'none' && s.opacity !== '0';",
            modal_id
        )
    except Exception:
        return False


def _esperar_modal(driver, modal_id, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: _modal_abierto(d, modal_id))


class UsuariosPage:
    TABLA            = (By.ID, "usersMainTable")
    FILAS_USUARIOS   = (By.CSS_SELECTOR, "#usersMainTable tbody tr")
    BTN_NUEVO        = (By.CSS_SELECTOR, ".btn-primary")
    INPUT_BUSCAR     = (By.ID, "tableSearch")
    VISIBLE_COUNT    = (By.ID, "visibleCount")
    MODAL_CREAR_ID   = "modalCrearUsuario"
    MODAL_DETALLE_ID = "modalVerDetalle"
    MODAL_TITLE      = (By.ID, "modalTitle")
    # Campos del modal
    CAMPO_DNI        = (By.ID, "dni")
    CAMPO_NOMBRE     = (By.ID, "nombre")
    CAMPO_CORREO     = (By.ID, "correo")
    CAMPO_PASSWORD   = (By.ID, "password")
    BTN_GUARDAR      = (By.CSS_SELECTOR, "button[onclick*='guardarUsuario']")
    BTN_CANCELAR     = (By.CSS_SELECTOR, "#modalCrearUsuario button[onclick*='cerrarModal']")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/configuracion/usuarios")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title, h2")))

    def obtener_filas(self):
        return [tr for tr in self.driver.find_elements(*self.FILAS_USUARIOS)
                if tr.is_displayed()]

    def tabla_visible(self):
        try:
            return self.driver.find_element(*self.TABLA).is_displayed()
        except Exception:
            return False

    def buscar(self, texto):
        campo = self.driver.find_element(*self.INPUT_BUSCAR)
        campo.clear()
        campo.send_keys(texto)
        time.sleep(0.5)

    def limpiar_busqueda(self):
        campo = self.driver.find_element(*self.INPUT_BUSCAR)
        self.driver.execute_script("arguments[0].value = '';", campo)
        campo.send_keys(" ")
        campo.send_keys("\b")
        time.sleep(0.3)

    def visible_count_texto(self):
        try:
            return self.driver.find_element(*self.VISIBLE_COUNT).text
        except Exception:
            return ""

    # ── Modal crear ────────────────────────────────────
    def abrir_modal_crear(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_CREAR_ID)
        time.sleep(0.3)

    def modal_crear_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_CREAR_ID)

    def modal_title_texto(self):
        return self.driver.find_element(*self.MODAL_TITLE).text

    def cerrar_modal_crear(self):
        try:
            btn = self.driver.find_element(*self.BTN_CANCELAR)
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script("cerrarModal();")
        time.sleep(0.4)

    def llenar_form_crear(self, dni, nombre, correo, password="Test1234!"):
        for field_id, valor in [
            ("dni", dni), ("nombre", nombre),
            ("correo", correo), ("password", password)
        ]:
            campo = self.driver.find_element(By.ID, field_id)
            self.driver.execute_script("arguments[0].value = '';", campo)
            campo.send_keys(valor)

    def guardar_usuario(self):
        btn = self.driver.find_element(*self.BTN_GUARDAR)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

    # ── Modal editar ───────────────────────────────────
    def abrir_modal_editar(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, "button[onclick*='abrirModalEditar']")
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_CREAR_ID)
        time.sleep(0.5)

    def modal_editar_titulo_correcto(self):
        titulo = self.modal_title_texto()
        return "editar" in titulo.lower() or "actualizar" in titulo.lower() or "modificar" in titulo.lower()

    # ── Modal detalle ──────────────────────────────────
    def abrir_modal_detalle(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, "button[onclick*='verDetallesTabla']")
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_DETALLE_ID)
        time.sleep(0.5)

    def modal_detalle_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_DETALLE_ID)

    def cerrar_modal_detalle(self):
        self.driver.execute_script(
            "var el = document.getElementById('modalVerDetalle');"
            "if (el) el.style.display = 'none';"
        )
        time.sleep(0.3)

    # ── Eliminar ───────────────────────────────────────
    def click_eliminar_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, "button[onclick*='eliminarUsuarioFisico']")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(1.5)


class ConfigDashboardPage:
    TITULO = (By.CSS_SELECTOR, ".section-title, h2")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/configuracion/dashboard")
        self.wait.until(EC.presence_of_element_located(self.TITULO))

    def carga_correctamente(self):
        try:
            self.driver.find_element(*self.TITULO)
            return True
        except Exception:
            return False
