from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class MeteorologiaPage:
    TITULO       = (By.CSS_SELECTOR, ".section-title")
    INPUT_APIKEY = (By.ID, "wx-apikey")
    INPUT_CIUDAD = (By.ID, "wx-city")
    BTN_CONECTAR = (By.CSS_SELECTOR, "button[onclick*='wxStart']")
    BTN_ACTUALIZAR = (By.CSS_SELECTOR, "button[onclick*='wxManual']")
    BTN_EXPORTAR = (By.CSS_SELECTOR, "button[onclick*='wxExportCSV']")
    BTN_LIMPIAR  = (By.CSS_SELECTOR, "button[onclick*='wxClear']")
    # Métricas
    WX_TEMP   = (By.ID, "wx-temp")
    WX_HUM    = (By.ID, "wx-hum")
    WX_PRESS  = (By.ID, "wx-press")
    WX_WIND   = (By.ID, "wx-wind")
    WX_CLOUDS = (By.ID, "wx-clouds")
    WX_VIS    = (By.ID, "wx-vis")
    WX_RAIN   = (By.ID, "wx-rain")
    WX_DEW    = (By.ID, "wx-dew")
    # Estado
    WX_PULSE       = (By.ID, "wx-pulse")
    WX_STATUS_TEXT = (By.ID, "wx-status-text")
    WX_LAST_UPDATE = (By.ID, "wx-last-update")
    WX_COUNT       = (By.ID, "wx-count")
    # Tabla histórica
    WX_TBODY  = (By.ID, "wx-tbody")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/admin/meteorologia/dashboard")
        self.wait.until(EC.presence_of_element_located(self.TITULO))

    def titulo_texto(self):
        return self.driver.find_element(*self.TITULO).text

    def input_apikey_presente(self):
        try:
            return self.driver.find_element(*self.INPUT_APIKEY).is_displayed()
        except Exception:
            return False

    def input_ciudad_presente(self):
        try:
            return self.driver.find_element(*self.INPUT_CIUDAD).is_displayed()
        except Exception:
            return False

    def btn_conectar_presente(self):
        try:
            return self.driver.find_element(*self.BTN_CONECTAR).is_displayed()
        except Exception:
            return False

    def btn_actualizar_presente(self):
        try:
            return self.driver.find_element(*self.BTN_ACTUALIZAR).is_displayed()
        except Exception:
            return False

    def btn_exportar_presente(self):
        try:
            return self.driver.find_element(*self.BTN_EXPORTAR).is_displayed()
        except Exception:
            return False

    def btn_limpiar_presente(self):
        try:
            return self.driver.find_element(*self.BTN_LIMPIAR).is_displayed()
        except Exception:
            return False

    def ciudad_default(self):
        campo = self.driver.find_element(*self.INPUT_CIUDAD)
        return campo.get_attribute("value") or campo.get_attribute("placeholder") or ""

    def metrica_elemento_presente(self, metric_id):
        try:
            el = self.driver.find_element(By.ID, metric_id)
            return el is not None
        except Exception:
            return False

    def tabla_historica_presente(self):
        try:
            tbody = self.driver.find_element(*self.WX_TBODY)
            return tbody is not None
        except Exception:
            return False

    def status_text_presente(self):
        try:
            self.driver.find_element(*self.WX_STATUS_TEXT)
            return True
        except Exception:
            return False

    def limpiar_datos(self):
        btn = self.driver.find_element(*self.BTN_LIMPIAR)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.5)
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(0.5)
