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


class GeneracionPage:
    TABLA       = (By.CSS_SELECTOR, ".gen-table")
    TBODY       = (By.ID, "gen-tbody")
    BTN_NUEVO   = (By.ID, "btn-open")
    MODAL_ID    = "modal-overlay"
    FILTRO_DESDE = (By.ID, "gen-f-desde")
    FILTRO_HASTA = (By.ID, "gen-f-hasta")
    BTN_FILTRAR  = (By.ID, "gen-f-aplicar")
    BTN_LIMPIAR  = (By.ID, "gen-f-limpiar")
    BTN_EXPORTAR = (By.ID, "gen-f-exportar")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/residuos/generacion")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title")))

    def obtener_filas(self):
        try:
            tbody = self.driver.find_element(*self.TBODY)
            return [tr for tr in tbody.find_elements(By.TAG_NAME, "tr")
                    if tr.get_attribute("data-fecha") or tr.get_attribute("data-idx")]
        except Exception:
            return []

    def abrir_modal_nuevo(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_ID)
        time.sleep(0.3)

    def modal_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_ID)

    def cerrar_modal(self):
        try:
            btn = self.driver.find_element(By.CSS_SELECTOR, "#modal-overlay .btn-secondary, #modal-overlay .btn-close")
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script(
                "var el = document.getElementById('modal-overlay');"
                "if (el) el.style.display = 'none';"
            )
        time.sleep(0.4)

    def filtrar_fechas(self, desde, hasta):
        campo_desde = self.driver.find_element(*self.FILTRO_DESDE)
        self.driver.execute_script("arguments[0].value = arguments[1];", campo_desde, desde)
        campo_hasta = self.driver.find_element(*self.FILTRO_HASTA)
        self.driver.execute_script("arguments[0].value = arguments[1];", campo_hasta, hasta)
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(*self.BTN_FILTRAR)
        )
        time.sleep(0.5)

    def limpiar_filtros(self):
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(*self.BTN_LIMPIAR)
        )
        time.sleep(0.3)

    def ver_detalle_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-ver")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

    def editar_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-edit")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)


class SubpaginaResiduosPage:
    """Page object genérico para comercializable, compostaje y matpel."""

    TABLA      = (By.CSS_SELECTOR, ".data-table, table")
    BTN_NUEVO  = (By.CSS_SELECTOR, ".action-bar .btn-primary, .btn-primary")

    def __init__(self, driver, base_url, ruta):
        self.driver = driver
        self.base_url = base_url
        self.ruta = ruta
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/residuos/{self.ruta}")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title, h2")))

    def tabla_visible(self):
        try:
            return self.driver.find_element(*self.TABLA).is_displayed()
        except Exception:
            return False

    def btn_nuevo_visible(self):
        try:
            return self.driver.find_element(*self.BTN_NUEVO).is_displayed()
        except Exception:
            return False
