from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time


def _modal_abierto(driver, modal_id):
    try:
        return driver.execute_script(
            "var el = document.getElementById(arguments[0]);"
            "if (!el) return false;"
            "return window.getComputedStyle(el).display !== 'none';",
            modal_id
        )
    except Exception:
        return False


def _esperar_modal(driver, modal_id, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: _modal_abierto(d, modal_id))


def _div_visible(driver, element_id):
    try:
        return driver.execute_script(
            "var el = document.getElementById(arguments[0]);"
            "if (!el) return false;"
            "return window.getComputedStyle(el).display !== 'none';",
            element_id
        )
    except Exception:
        return False


class CompromisosPage:
    TABLA             = (By.CSS_SELECTOR, ".compromisos-table")
    FILAS             = (By.CSS_SELECTOR, ".compromisos-table tbody tr")
    BADGE_COUNT       = (By.CSS_SELECTOR, ".badge-count")
    BTN_EXPORTAR      = (By.CSS_SELECTOR, ".btn-export")
    BTN_VER_EVIDENCIA = (By.CSS_SELECTOR, ".btn-evidencia-ok")
    POPOVER           = (By.CSS_SELECTOR, ".versiones-popover")
    ITEMS_POPOVER     = (By.CSS_SELECTOR, ".versiones-popover__item")
    MODAL_ID          = "modalEditarCompromiso"
    MODAL_EDITAR      = (By.ID, "modalEditarCompromiso")
    CAMPO_NOMBRE      = (By.ID, "editComp_nombre")
    CAMPO_ENTIDAD     = (By.ID, "editComp_entidad")
    SEL_SUPERVISOR    = (By.ID, "editComp_supervisor")
    CAMPO_OBS         = (By.ID, "editComp_observaciones")
    BTN_GUARDAR       = (By.CSS_SELECTOR, "#modalEditarCompromiso .btn-primary")
    BTN_CANCELAR      = (By.CSS_SELECTOR, "#modalEditarCompromiso .btn-secondary")
    ESTADO_GUARDADO   = (By.ID, "editComp_estado")
    DIV_CON_EVIDENCIA = (By.ID, "editComp_conEvidencia")
    DIV_SIN_EVIDENCIA = (By.ID, "editComp_sinEvidencia")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/compromisos")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def ir_con_periodo(self, mes, anio):
        self.driver.get(f"{self.base_url}/admin/compromisos?mes={mes}&anio={anio}")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def obtener_total_registros(self):
        return int(self.driver.find_element(*self.BADGE_COUNT).text.split()[0])

    def obtener_filas(self):
        return self.driver.find_elements(*self.FILAS)

    def tiene_evidencia_fila(self, indice=0):
        filas = self.obtener_filas()
        if indice >= len(filas):
            return False
        try:
            filas[indice].find_element(*self.BTN_VER_EVIDENCIA)
            return True
        except Exception:
            return False

    def click_ver_evidencia(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(*self.BTN_VER_EVIDENCIA)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

    def popover_visible(self):
        try:
            return self.driver.find_element(*self.POPOVER).is_displayed()
        except Exception:
            return False

    def obtener_versiones_en_popover(self):
        self.wait.until(EC.presence_of_element_located(self.POPOVER))
        return self.driver.find_elements(*self.ITEMS_POPOVER)

    def abrir_modal_editar(self, indice=0):
        filas = self.obtener_filas()
        btn = None
        for selector in [
            "button[onclick*='abrirEditarCompromiso']",
            "button[data-comp]",
            ".btn-icon-edit",
        ]:
            try:
                btn = filas[indice].find_element(By.CSS_SELECTOR, selector)
                break
            except Exception:
                continue
        if btn is None:
            raise Exception(f"No se encontró botón editar en fila {indice}")
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_ID)
        time.sleep(0.3)

    def modal_esta_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_ID)

    def obtener_nombre_en_modal(self):
        return self.driver.find_element(*self.CAMPO_NOMBRE).get_attribute("value")

    def obtener_entidad_en_modal(self):
        return self.driver.find_element(*self.CAMPO_ENTIDAD).get_attribute("value")

    def escribir_observaciones(self, texto):
        campo = self.driver.find_element(*self.CAMPO_OBS)
        self.driver.execute_script("arguments[0].value = '';", campo)
        campo.send_keys(texto)

    def guardar_modal(self):
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(*self.BTN_GUARDAR)
        )
        # Esperar que aparezca texto Y que no sea "Guardando..."
        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script(
                "var el = document.getElementById('editComp_estado');"
                "if (!el) return false;"
                "var t = el.innerText.trim();"
                "return t !== '' && t.indexOf('Guardando') === -1;"
            )
        )

    def estado_guardado_texto(self):
        return self.driver.execute_script(
            "var el = document.getElementById('editComp_estado');"
            "return el ? el.innerText.trim() : '';"
        )

    def cancelar_modal(self):
        self.driver.execute_script("cerrarEditarCompromiso();")
        time.sleep(0.4)

    def modal_tiene_evidencia(self):
        return _div_visible(self.driver, "editComp_conEvidencia")

    def modal_sin_evidencia(self):
        return _div_visible(self.driver, "editComp_sinEvidencia")

    def subir_archivo_modal(self, ruta):
        input_file = self.driver.find_element(By.ID, "editComp_archivo")
        input_file.send_keys(ruta)
        time.sleep(1)

    def obtener_label_archivo(self):
        return self.driver.execute_script(
            "var el = document.getElementById('editComp_archivoLabel');"
            "return el ? el.innerText.trim() : '';"
        )