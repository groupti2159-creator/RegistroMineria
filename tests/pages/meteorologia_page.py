from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MeteorologiaPage:
    TITULO       = (By.CSS_SELECTOR, ".section-title")
    INPUT_APIKEY = (By.ID, "wx-api-key")
    INPUT_CIUDAD = (By.ID, "wx-city")
    BTN_CONECTAR = (By.ID, "wx-connect")
    BTN_EXPORTAR = (By.CSS_SELECTOR, "[id*='export'], .btn-export, button[onclick*='exportar']")
    METRICAS     = (By.CSS_SELECTOR, ".metric-card, .weather-card, .wx-metric")
    ESTADO_DOT   = (By.CSS_SELECTOR, ".status-dot, .pulse-dot, [class*='status']")

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

    def tiene_metricas(self):
        return len(self.driver.find_elements(*self.METRICAS)) > 0

    def tiene_input_configuracion(self):
        """Verifica que la página tenga la sección de configuración de la API."""
        return self.input_apikey_presente() or self.input_ciudad_presente()
