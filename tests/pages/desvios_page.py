from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
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


class DesviosPage:
    TABLA        = (By.CSS_SELECTOR, ".data-table")
    FILAS        = (By.CSS_SELECTOR, ".data-table tbody tr")
    FILTER_COUNT = (By.CSS_SELECTOR, ".filter-count")
    FILTER_SEL   = (By.CSS_SELECTOR, ".filter-select")
    BTN_EXPORTAR = (By.CSS_SELECTOR, ".btn-export")
    BTN_NUEVO    = (By.CSS_SELECTOR, ".btn-primary")
    MODAL_CREAR  = "modalCrear"
    ESTADO_BADGES = (By.CSS_SELECTOR, ".estado-badge")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/registrar")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def obtener_filas(self):
        return self.driver.find_elements(*self.FILAS)

    def obtener_total_texto(self):
        return self.driver.find_element(*self.FILTER_COUNT).text

    def filtrar_por_estado(self, valor):
        sel = self.driver.find_element(*self.FILTER_SEL)
        Select(sel).select_by_value(valor)
        time.sleep(0.8)

    def abrir_modal_crear(self):
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(*self.BTN_NUEVO)
        )
        _esperar_modal(self.driver, self.MODAL_CREAR)
        time.sleep(0.3)

    def modal_crear_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_CREAR)

    def cerrar_modal_crear(self):
        self.driver.execute_script(f"cerrarModal('{self.MODAL_CREAR}');")
        time.sleep(0.4)

    def abrir_detalle_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-blue")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    def click_editar_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-yellow")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)

    def obtener_estados_visibles(self):
        return [b.text.strip() for b in self.driver.find_elements(*self.ESTADO_BADGES)]

    def exportar_href(self):
        return self.driver.find_element(*self.BTN_EXPORTAR).get_attribute("href")


class DesviosDashboardPage:
    STAT_CARDS = (By.CSS_SELECTOR, ".stat-card, .stats-card, .kpi-card")
    TABLA      = (By.CSS_SELECTOR, ".data-table, table")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/dashboard")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title, h2")))
