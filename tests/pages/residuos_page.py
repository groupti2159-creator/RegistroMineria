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


def _obtener_filas_tbody(driver, tbody_id):
    try:
        tbody = driver.find_element(By.ID, tbody_id)
        return [tr for tr in tbody.find_elements(By.TAG_NAME, "tr")
                if tr.get_attribute("data-fecha") or tr.get_attribute("data-id")]
    except Exception:
        return []


class GeneracionPage:
    TABLA        = (By.CSS_SELECTOR, ".gen-table")
    TBODY        = (By.ID, "gen-tbody")
    BTN_NUEVO    = (By.ID, "btn-open")
    MODAL_ID     = "modal-overlay"
    MODAL_DET_ID = "modal-detalle-overlay"
    FILTRO_DESDE  = (By.ID, "gen-f-desde")
    FILTRO_HASTA  = (By.ID, "gen-f-hasta")
    BTN_FILTRAR   = (By.ID, "gen-f-aplicar")
    BTN_LIMPIAR   = (By.ID, "gen-f-limpiar")
    BTN_EXPORTAR  = (By.ID, "gen-f-exportar")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/residuos/generacion")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title")))

    def obtener_filas(self):
        return _obtener_filas_tbody(self.driver, "gen-tbody")

    def abrir_modal_nuevo(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_ID)
        time.sleep(0.3)

    def modal_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_ID)

    def cerrar_modal(self):
        try:
            btn = self.driver.find_element(
                By.CSS_SELECTOR, "#modal-overlay .btn-secondary, #modal-overlay .btn-close"
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script(
                "var el = document.getElementById('modal-overlay');"
                "if (el) el.style.display = 'none';"
            )
        time.sleep(0.4)

    def filtrar_fechas(self, desde, hasta):
        campo = self.driver.find_element(*self.FILTRO_DESDE)
        self.driver.execute_script("arguments[0].value = arguments[1];", campo, desde)
        campo = self.driver.find_element(*self.FILTRO_HASTA)
        self.driver.execute_script("arguments[0].value = arguments[1];", campo, hasta)
        self.driver.execute_script(
            "arguments[0].click();", self.driver.find_element(*self.BTN_FILTRAR)
        )
        time.sleep(0.5)

    def limpiar_filtros(self):
        self.driver.execute_script(
            "arguments[0].click();", self.driver.find_element(*self.BTN_LIMPIAR)
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
        _esperar_modal(self.driver, self.MODAL_ID)
        time.sleep(0.4)

    def eliminar_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-del, .btn-icon-danger, [onclick*='eliminar']")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(1.5)

    def modal_detalle_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_DET_ID)

    def cerrar_modal_detalle(self):
        try:
            btn = self.driver.find_element(
                By.CSS_SELECTOR, "#modal-detalle-overlay .btn-secondary, #modal-detalle-overlay .btn-close"
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script(
                "var el = document.getElementById('modal-detalle-overlay');"
                "if (el) el.style.display = 'none';"
            )
        time.sleep(0.4)


class SubpaginaResiduosPage:
    """Page object para comercializable, compostaje y matpel."""

    _CONFIG = {
        "comercializable": {
            "ruta": "comercializable",
            "modal_id": "modal-com-overlay",
            "btn_open": "btn-open-com",
            "btn_save": "btn-save-com",
            "btn_cancel": "btn-cancel-com",
            "tbody_id": "com-tbody",
            "f_desde": "com-f-desde",
            "f_hasta": "com-f-hasta",
            "f_aplicar": "com-f-aplicar",
            "f_limpiar": "com-f-limpiar",
            "f_exportar": "com-f-exportar",
            "campo_fecha": "com-fecha",
            "campo_peso": "com-peso",
            "campo_precio": "com-precio",
        },
        "compostaje": {
            "ruta": "compostaje",
            "modal_id": "modal-comp-overlay",
            "btn_open": "btn-open-comp",
            "btn_save": "btn-save-comp",
            "btn_cancel": "btn-cancel-comp",
            "tbody_id": "comp-tbody",
            "f_desde": "comp-f-desde",
            "f_hasta": "comp-f-hasta",
            "f_aplicar": "comp-f-aplicar",
            "f_limpiar": "comp-f-limpiar",
            "f_exportar": "comp-f-exportar",
            "campo_fecha": "comp-fecha",
            "campo_peso": "comp-peso",
            "campo_precio": "comp-precio",
        },
        "matpel": {
            "ruta": "matpel",
            "modal_id": "modal-mat-overlay",
            "btn_open": "btn-open-mat",
            "btn_save": "btn-save-mat",
            "btn_cancel": "btn-cancel-mat",
            "tbody_id": "mat-tbody",
            "f_desde": "mat-f-desde",
            "f_hasta": "mat-f-hasta",
            "f_aplicar": "mat-f-aplicar",
            "f_limpiar": "mat-f-limpiar",
            "f_exportar": "mat-f-exportar",
            "campo_fecha": "mat-fecha",
            "campo_peso": "mat-peso",
            "campo_precio": "mat-precio",
        },
    }

    def __init__(self, driver, base_url, nombre):
        self.driver = driver
        self.base_url = base_url
        self.cfg = self._CONFIG[nombre]
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/residuos/{self.cfg['ruta']}")
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".section-title, h2")))

    def obtener_filas(self):
        return _obtener_filas_tbody(self.driver, self.cfg["tbody_id"])

    def tabla_visible(self):
        try:
            tbody = self.driver.find_element(By.ID, self.cfg["tbody_id"])
            return tbody.is_displayed()
        except Exception:
            return False

    def btn_nuevo_visible(self):
        try:
            return self.driver.find_element(By.ID, self.cfg["btn_open"]).is_displayed()
        except Exception:
            return False

    def abrir_modal_nuevo(self):
        btn = self.wait.until(EC.element_to_be_clickable((By.ID, self.cfg["btn_open"])))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.cfg["modal_id"])
        time.sleep(0.3)

    def modal_abierto(self):
        return _modal_abierto(self.driver, self.cfg["modal_id"])

    def cerrar_modal(self):
        try:
            btn = self.driver.find_element(By.ID, self.cfg["btn_cancel"])
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            self.driver.execute_script(
                f"var el = document.getElementById('{self.cfg[\"modal_id\"]}');"
                "if (el) el.style.display = 'none';"
            )
        time.sleep(0.4)

    def llenar_form(self, fecha="2026-01-15", peso="100", precio="50"):
        self.driver.execute_script(
            f"document.getElementById('{self.cfg[\"campo_fecha\"]}').value = arguments[0];", fecha
        )
        try:
            campo_peso = self.driver.find_element(By.ID, self.cfg["campo_peso"])
            self.driver.execute_script("arguments[0].value = '';", campo_peso)
            campo_peso.send_keys(peso)
        except Exception:
            pass
        try:
            campo_precio = self.driver.find_element(By.ID, self.cfg["campo_precio"])
            self.driver.execute_script("arguments[0].value = '';", campo_precio)
            campo_precio.send_keys(precio)
        except Exception:
            pass

    def guardar(self):
        btn = self.driver.find_element(By.ID, self.cfg["btn_save"])
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

    def filtrar_fechas(self, desde, hasta):
        campo = self.driver.find_element(By.ID, self.cfg["f_desde"])
        self.driver.execute_script("arguments[0].value = arguments[1];", campo, desde)
        campo = self.driver.find_element(By.ID, self.cfg["f_hasta"])
        self.driver.execute_script("arguments[0].value = arguments[1];", campo, hasta)
        self.driver.execute_script(
            "arguments[0].click();", self.driver.find_element(By.ID, self.cfg["f_aplicar"])
        )
        time.sleep(0.5)

    def limpiar_filtros(self):
        self.driver.execute_script(
            "arguments[0].click();", self.driver.find_element(By.ID, self.cfg["f_limpiar"])
        )
        time.sleep(0.3)

    def exportar_btn_visible(self):
        try:
            return self.driver.find_element(By.ID, self.cfg["f_exportar"]).is_displayed()
        except Exception:
            return False

    def abrir_modal_editar(self, indice=0):
        filas = self.obtener_filas()
        if not filas:
            return False
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-edit, .btn-icon-edit, [onclick*='edit']")
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.cfg["modal_id"])
        time.sleep(0.4)
        return True

    def eliminar_fila(self, indice=0):
        filas = self.obtener_filas()
        if not filas:
            return False
        btn = filas[indice].find_element(
            By.CSS_SELECTOR, ".btn-del, .btn-icon-danger, [onclick*='eliminar']"
        )
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(1.5)
        return True
