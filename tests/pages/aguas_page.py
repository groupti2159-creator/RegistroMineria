# ════════════════════════════════════════════════════════
#  ecoSupervisor — tests/pages/aguas_page.py
#  Page Object: Gestión de Aguas — Monitoreo + Reporte ANA
# ════════════════════════════════════════════════════════

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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


def _cerrar_modal(driver, modal_id, btn_selector):
    """Cierra un modal usando JS click."""
    btn = driver.find_element(By.CSS_SELECTOR, btn_selector)
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(0.3)


class MonitoreoPage:

    TABLA           = (By.CSS_SELECTOR, ".agua-table")
    SEL_TIPO        = (By.ID, "selectTipo")
    INPUT_BUSCAR    = (By.ID, "inputBuscar")
    BTN_LIMPIAR     = (By.CSS_SELECTOR, ".btn-secondary")
    BADGE_COUNT     = (By.ID, "contadorTabla")
    BTN_NUEVO_EF    = (By.XPATH, "//button[contains(.,'Nuevo Registro Efluentes')]")
    BTN_NUEVO_PTARD = (By.XPATH, "//button[contains(.,'Nuevo Registro PTARD')]")
    BTN_NUEVO_PTAP  = (By.XPATH, "//button[contains(.,'Nuevo Registro PTAP')]")

    def __init__(self, driver, base_url):
        self.driver   = driver
        self.base_url = base_url
        self.wait     = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/aguas")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def cambiar_tipo(self, tipo):
        Select(self.driver.find_element(*self.SEL_TIPO)).select_by_value(tipo)
        time.sleep(0.5)

    def buscar(self, texto):
        campo = self.driver.find_element(*self.INPUT_BUSCAR)
        campo.clear()
        campo.send_keys(texto)
        time.sleep(0.5)

    def limpiar_filtros(self):
        self.driver.find_element(*self.BTN_LIMPIAR).click()

    def abrir_modal_efluentes(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO_EF))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, "modal-efluentes")

    def modal_efluentes_abierto(self):
        return _modal_abierto(self.driver, "modal-efluentes")

    def cancelar_efluente(self):
        _cerrar_modal(self.driver, "modal-efluentes", "#modal-efluentes .btn-secondary")

    def abrir_modal_ptard(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO_PTARD))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, "modal-ptard")

    def cerrar_modal_ptard(self):
        _cerrar_modal(self.driver, "modal-ptard", "#modal-ptard .btn-secondary")

    def abrir_modal_ptap(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO_PTAP))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, "modal-ptap")

    def cerrar_modal_ptap(self):
        _cerrar_modal(self.driver, "modal-ptap", "#modal-ptap .btn-secondary")

    def obtener_filas_visibles(self, tipo="efluentes"):
        tbody = self.driver.find_element(By.ID, f"tbody-{tipo}")
        return [tr for tr in tbody.find_elements(By.TAG_NAME, "tr")
                if tr.is_displayed() and tr.get_attribute("data-search")]


class ReporteANAPage:

    TABLA        = (By.CSS_SELECTOR, ".ana-table")
    BADGE_COUNT  = (By.ID, "contadorTabla")
    INPUT_BUSCAR = (By.ID, "inputBuscar")
    FECHA_INI    = (By.ID, "filtroFechaIni")
    FECHA_FIN    = (By.ID, "filtroFechaFin")
    BTN_LIMPIAR  = (By.CSS_SELECTOR, ".btn-secondary")
    BTN_NUEVO    = (By.CSS_SELECTOR, ".action-bar .btn-primary")
    CAMPO_FECHA     = (By.ID, "ana_fecha")
    CAMPO_TIEMPO    = (By.ID, "ana_tiempo")
    CAMPO_CONT_INI  = (By.ID, "ana_cont_ini")
    CAMPO_CONT_FIN  = (By.ID, "ana_cont_fin")
    CAMPO_VOLUMEN   = (By.ID, "ana_volumen")
    CAMPO_CAUDAL    = (By.ID, "ana_caudal")
    BTN_GUARDAR  = (By.CSS_SELECTOR, "#modalANA .btn-primary")
    BTN_CANCELAR = (By.CSS_SELECTOR, "#modalANA .btn-secondary")
    ESTADO       = (By.ID, "anaEstado")

    def __init__(self, driver, base_url):
        self.driver   = driver
        self.base_url = base_url
        self.wait     = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/ana")
        self.wait.until(EC.presence_of_element_located(self.TABLA))

    def abrir_modal(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_NUEVO))
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, "modalANA")
        time.sleep(0.3)

    def modal_abierto(self):
        return _modal_abierto(self.driver, "modalANA")

    def llenar_reporte(self, fecha, cont_ini, cont_fin, tiempo="24 horas"):
        campo_fecha = self.driver.find_element(*self.CAMPO_FECHA)
        self.driver.execute_script("arguments[0].value = '';", campo_fecha)
        campo_fecha.send_keys(fecha)

        campo_tiempo = self.driver.find_element(*self.CAMPO_TIEMPO)
        campo_tiempo.send_keys(Keys.CONTROL + "a")
        campo_tiempo.send_keys(tiempo)

        campo_ini = self.driver.find_element(*self.CAMPO_CONT_INI)
        self.driver.execute_script("arguments[0].value = '';", campo_ini)
        campo_ini.send_keys(str(cont_ini))
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input'));", campo_ini
        )

        campo_fin = self.driver.find_element(*self.CAMPO_CONT_FIN)
        self.driver.execute_script("arguments[0].value = '';", campo_fin)
        campo_fin.send_keys(str(cont_fin))
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input'));", campo_fin
        )
        time.sleep(0.5)

    def obtener_volumen_calculado(self):
        return self.driver.find_element(*self.CAMPO_VOLUMEN).get_attribute("value")

    def obtener_caudal_calculado(self):
        return self.driver.find_element(*self.CAMPO_CAUDAL).get_attribute("value")

    def guardar(self):
        btn = self.driver.find_element(*self.BTN_GUARDAR)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", btn)
        self.wait.until(EC.visibility_of_element_located(self.ESTADO))

    def cancelar(self):
        btn = self.driver.find_element(*self.BTN_CANCELAR)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)

    def estado_texto(self):
        return self.driver.find_element(*self.ESTADO).text

    def obtener_filas(self):
        tbody = self.driver.find_element(By.ID, "tbody-ana")
        return [tr for tr in tbody.find_elements(By.TAG_NAME, "tr")
                if tr.get_attribute("data-fecha")]

    def obtener_headers(self):
        headers = self.driver.find_elements(
            By.CSS_SELECTOR, ".ana-table thead th"
        )
        textos = []
        for h in headers:
            texto = self.driver.execute_script(
                "return arguments[0].innerText || arguments[0].textContent;", h
            )
            textos.append(texto.replace("\n", " ").strip())
        return textos

    def filtrar_fechas(self, fecha_ini, fecha_fin):
        campo = self.driver.find_element(*self.FECHA_INI)
        self.driver.execute_script("arguments[0].value = arguments[1];", campo, fecha_ini)
        campo = self.driver.find_element(*self.FECHA_FIN)
        self.driver.execute_script("arguments[0].value = arguments[1];", campo, fecha_fin)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change'));",
            self.driver.find_element(*self.FECHA_FIN)
        )
        time.sleep(0.5)

    def limpiar_filtros(self):
        self.driver.find_element(*self.BTN_LIMPIAR).click()