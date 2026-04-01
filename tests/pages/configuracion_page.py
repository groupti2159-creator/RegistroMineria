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
    TABLA           = (By.CSS_SELECTOR, ".data-table, table")
    FILAS_USUARIOS  = (By.CSS_SELECTOR, "tbody tr")
    BTN_NUEVO       = (By.CSS_SELECTOR, ".btn-primary")
    MODAL_CREAR_ID  = "modalCrearUsuario"
    MODAL_DETALLE_ID = "modalVerDetalle"
    CAMPO_NOMBRE    = (By.ID, "nombre")
    CAMPO_DNI       = (By.ID, "dni")
    CAMPO_CORREO    = (By.ID, "correo")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/configuracion/usuarios")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title, h2")))

    def obtener_filas(self):
        return self.driver.find_elements(*self.FILAS_USUARIOS)

    def tabla_visible(self):
        try:
            return self.driver.find_element(*self.TABLA).is_displayed()
        except Exception:
            return False

    def abrir_modal_crear(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_CREAR_ID)
        time.sleep(0.3)

    def modal_crear_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_CREAR_ID)

    def cerrar_modal_crear(self):
        try:
            btn = self.driver.find_element(
                By.CSS_SELECTOR, f"#{self.MODAL_CREAR_ID} .btn-secondary, #{self.MODAL_CREAR_ID} .btn-close"
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script(
                f"var el = document.getElementById('{self.MODAL_CREAR_ID}');"
                "if (el) el.style.display = 'none';"
            )
        time.sleep(0.4)

    def ver_detalle_fila(self, indice=0):
        filas = self.obtener_filas()
        try:
            btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-blue, .btn-icon, button[onclick*='ver']")
            self.driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.8)
        except Exception:
            pass

    def modal_detalle_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_DETALLE_ID)


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
