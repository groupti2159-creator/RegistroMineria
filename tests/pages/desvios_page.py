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
    TABLA         = (By.CSS_SELECTOR, ".data-table")
    FILAS         = (By.CSS_SELECTOR, ".data-table tbody tr")
    FILTER_COUNT  = (By.CSS_SELECTOR, ".filter-count")
    FILTER_SEL    = (By.CSS_SELECTOR, ".filter-select")
    BTN_EXPORTAR  = (By.CSS_SELECTOR, ".btn-export")
    BTN_NUEVO     = (By.CSS_SELECTOR, ".action-bar .btn-primary")
    ESTADO_BADGES = (By.CSS_SELECTOR, ".estado-badge")

    MODAL_CREAR   = "modalCrear"
    MODAL_EDITAR  = "modalEditar"
    MODAL_DETALLE = "modalDetalle"

    # Campos del modal crear
    CAMPO_FECHA_INICIO = (By.ID, "fecha_inicio")
    CAMPO_FECHA_EJEC   = (By.NAME, "fecha_ejecucion")
    SEL_AREA_REP       = (By.NAME, "area_reportante")
    SEL_UBICACION      = (By.NAME, "ubicacion")
    SEL_RIESGO         = (By.NAME, "riesgo")
    SEL_TIPO           = (By.NAME, "tipo")
    CAMPO_DESCRIPCION  = (By.NAME, "descripcion")
    CAMPO_ACCION       = (By.NAME, "accion")
    SEL_AREA_RES       = (By.NAME, "area_responsable")
    CAMPO_PERSONAL     = (By.NAME, "personal_responsable")
    CAMPO_DNI          = (By.NAME, "dni_responsable")

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

    def opciones_estado(self):
        sel = self.driver.find_element(*self.FILTER_SEL)
        return [o.get_attribute("value") for o in sel.find_elements(By.TAG_NAME, "option")
                if o.get_attribute("value")]

    # ── Modal Crear ────────────────────────────────────
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

    def llenar_form_crear(self, fecha, area_rep_idx=1, ubicacion_idx=1,
                          riesgo_idx=1, tipo_idx=1, descripcion="Test desc",
                          accion="Test accion", personal="Test Personal", dni="12345678"):
        self.driver.execute_script(
            "document.getElementById('fecha_inicio').value = arguments[0];", fecha
        )
        self.driver.execute_script(
            "document.querySelector('[name=fecha_ejecucion]').value = arguments[0];", fecha
        )
        for selector, idx in [
            (self.SEL_AREA_REP, area_rep_idx),
            (self.SEL_UBICACION, ubicacion_idx),
            (self.SEL_RIESGO, riesgo_idx),
            (self.SEL_TIPO, tipo_idx),
        ]:
            try:
                Select(self.driver.find_element(*selector)).select_by_index(idx)
            except Exception:
                pass
        for selector, valor in [
            (self.CAMPO_DESCRIPCION, descripcion),
            (self.CAMPO_ACCION, accion),
            (self.CAMPO_PERSONAL, personal),
            (self.CAMPO_DNI, dni),
        ]:
            campo = self.driver.find_element(*selector)
            self.driver.execute_script("arguments[0].value = '';", campo)
            campo.send_keys(valor)

    def enviar_form_crear(self):
        btn = self.driver.find_element(By.ID, "btnGuardarReporte")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)

    # ── Modal Editar ───────────────────────────────────
    def abrir_modal_editar(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-yellow")
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_EDITAR)
        time.sleep(0.5)

    def modal_editar_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_EDITAR)

    def cerrar_modal_editar(self):
        self.driver.execute_script(f"cerrarModal('{self.MODAL_EDITAR}');")
        time.sleep(0.4)

    def edit_campo_valor(self, field_id):
        return self.driver.find_element(By.ID, field_id).get_attribute("value")

    # ── Modal Detalle ──────────────────────────────────
    def abrir_modal_detalle(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-blue")
        self.driver.execute_script("arguments[0].click();", btn)
        _esperar_modal(self.driver, self.MODAL_DETALLE)
        time.sleep(0.5)

    def modal_detalle_abierto(self):
        return _modal_abierto(self.driver, self.MODAL_DETALLE)

    def cerrar_modal_detalle(self):
        self.driver.execute_script(f"cerrarModal('{self.MODAL_DETALLE}');")
        time.sleep(0.4)

    # ── Eliminar ───────────────────────────────────────
    def click_eliminar_fila(self, indice=0):
        filas = self.obtener_filas()
        btn = filas[indice].find_element(By.CSS_SELECTOR, ".btn-icon-danger")
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(1.5)

    # ── Exportar ───────────────────────────────────────
    def exportar_href(self):
        return self.driver.find_element(*self.BTN_EXPORTAR).get_attribute("href")

    def obtener_estados_visibles(self):
        return [b.text.strip() for b in self.driver.find_elements(*self.ESTADO_BADGES)]


class DesviosDashboardPage:
    TITULO     = (By.CSS_SELECTOR, ".section-title, h2")
    MODAL_DET  = "modalDetalle"

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/dashboard")
        self.wait.until(EC.presence_of_element_located(self.TITULO))

    def carga_correctamente(self):
        try:
            self.driver.find_element(*self.TITULO)
            return True
        except Exception:
            return False
