# ════════════════════════════════════════════════════════
#  ecoSupervisor — tests/pages/compromisos_page.py
#  Page Object: módulo Compromisos
# ════════════════════════════════════════════════════════

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time


def _modal_abierto(driver, modal_id):
    """Verifica si un modal está visible chequeando su style (display:flex)."""
    try:
        modal = driver.find_element(By.ID, modal_id)
        style = modal.get_attribute("style") or ""
        return "none" not in style and modal.is_displayed()
    except Exception:
        return False


def _esperar_modal(driver, modal_id, timeout=10):
    """Espera hasta que el modal esté visible."""
    WebDriverWait(driver, timeout).until(
        lambda d: _modal_abierto(d, modal_id)
    )


class CompromisosPage:

    # ── Tabla ────────────────────────────────────────────
    TABLA             = (By.CSS_SELECTOR, ".compromisos-table")
    FILAS             = (By.CSS_SELECTOR, ".compromisos-table tbody tr")
    BADGE_COUNT       = (By.CSS_SELECTOR, ".badge-count")
    SEL_MES           = (By.ID, "selMes")
    SEL_ANIO          = (By.ID, "selAnio")
    BTN_APLICAR       = (By.CSS_SELECTOR, ".btn-secondary")
    BTN_EXPORTAR      = (By.CSS_SELECTOR, ".btn-export")

    # ── Evidencia ────────────────────────────────────────
    BTN_VER_EVIDENCIA = (By.CSS_SELECTOR, ".btn-evidencia-ok")
    POPOVER           = (By.CSS_SELECTOR, ".versiones-popover")
    ITEMS_POPOVER     = (By.CSS_SELECTOR, ".versiones-popover__item")

    # ── Modal editar ─────────────────────────────────────
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
        self.driver   = driver
        self.base_url = base_url
        self.wait     = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/compromisos")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def ir_con_periodo(self, mes, anio):
        self.driver.get(f"{self.base_url}/admin/compromisos?mes={mes}&anio={anio}")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def obtener_total_registros(self):
        texto = self.driver.find_element(*self.BADGE_COUNT).text
        return int(texto.split()[0])

    def cambiar_periodo(self, mes, anio):
        Select(self.driver.find_element(*self.SEL_MES)).select_by_value(str(mes))
        Select(self.driver.find_element(*self.SEL_ANIO)).select_by_value(str(anio))
        self.driver.find_element(*self.BTN_APLICAR).click()
        self.wait.until(EC.presence_of_element_located(self.TABLA))

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
        btn   = filas[indice].find_element(*self.BTN_VER_EVIDENCIA)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

    def popover_visible(self):
        try:
            pop = self.driver.find_element(*self.POPOVER)
            return pop.is_displayed()
        except Exception:
            return False

    def obtener_versiones_en_popover(self):
        self.wait.until(EC.presence_of_element_located(self.POPOVER))
        return self.driver.find_elements(*self.ITEMS_POPOVER)

    def abrir_modal_editar(self, indice=0):
        filas = self.obtener_filas()
        btn   = filas[indice].find_element(
            By.CSS_SELECTOR, "button[onclick*='abrirEditarCompromiso']"
        )
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_ID)

    def modal_esta_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_ID)

    def obtener_nombre_en_modal(self):
        return self.driver.find_element(*self.CAMPO_NOMBRE).get_attribute("value")

    def obtener_entidad_en_modal(self):
        return self.driver.find_element(*self.CAMPO_ENTIDAD).get_attribute("value")

    def seleccionar_supervisor(self, texto):
        Select(self.driver.find_element(*self.SEL_SUPERVISOR)).select_by_visible_text(texto)

    def escribir_observaciones(self, texto):
        campo = self.driver.find_element(*self.CAMPO_OBS)
        campo.clear()
        campo.send_keys(texto)

    def guardar_modal(self):
        btn = self.driver.find_element(*self.BTN_GUARDAR)
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.visibility_of_element_located(self.ESTADO_GUARDADO))

    def cancelar_modal(self):
        btn = self.driver.find_element(*self.BTN_CANCELAR)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.4)

    def estado_guardado_texto(self):
        return self.driver.find_element(*self.ESTADO_GUARDADO).text

    def modal_tiene_evidencia(self):
        div = self.driver.find_element(*self.DIV_CON_EVIDENCIA)
        return div.is_displayed()