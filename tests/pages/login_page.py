# ════════════════════════════════════════════════════════
#  ecoSupervisor — tests/pages/login_page.py
#  Page Object: pantalla de login + selección de rol
# ════════════════════════════════════════════════════════

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class LoginPage:

    # ── Login ────────────────────────────────────────────
    INPUT_DNI      = (By.NAME, "dni")
    INPUT_PASSWORD = (By.NAME, "password")
    BTN_INGRESAR   = (By.CSS_SELECTOR, "button[type='submit']")

    # ── Selección de rol (label visible, no el radio oculto) ─
    LABEL_ROL      = (By.CSS_SELECTOR, ".rol-selector-card")
    BTN_CONFIRMAR  = (By.CSS_SELECTOR, "button[type='submit']")

    # ── Confirmación de login exitoso ────────────────────
    SIDEBAR        = (By.CSS_SELECTOR, ".sidebar")

    def __init__(self, driver, base_url):
        self.driver   = driver
        self.base_url = base_url
        self.wait     = WebDriverWait(driver, 10)

    def ir(self):
        self.driver.get(f"{self.base_url}/login")
        self.wait.until(EC.presence_of_element_located(self.INPUT_DNI))

    def iniciar_sesion(self, dni, password):
        self.driver.find_element(*self.INPUT_DNI).clear()
        self.driver.find_element(*self.INPUT_DNI).send_keys(dni)
        self.driver.find_element(*self.INPUT_PASSWORD).clear()
        self.driver.find_element(*self.INPUT_PASSWORD).send_keys(password)
        self.driver.find_element(*self.BTN_INGRESAR).click()

        time.sleep(1.5)

        # Si hay pantalla de selección de rol
        if "seleccionar_rol" in self.driver.current_url or "rol" in self.driver.current_url:
            labels = self.driver.find_elements(*self.LABEL_ROL)
            if labels:
                # JS click porque el radio input está oculto por el estilo del label
                self.driver.execute_script("arguments[0].click();", labels[0])
                time.sleep(0.5)
            self.driver.find_element(*self.BTN_CONFIRMAR).click()
            time.sleep(1)

        # Esperar sidebar como confirmación de login exitoso
        self.wait.until(EC.presence_of_element_located(self.SIDEBAR))

    def esta_logueado(self):
        return "/login" not in self.driver.current_url