"""Login no portal FGTS Digital."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

FGTS_URL = "https://fgts.caixa.gov.br"
TIMEOUT = 30


def login_fgts(driver, usuario: str, senha: str) -> None:
    logger.info("Iniciando login FGTS Digital")
    driver.get(FGTS_URL)
    wait = WebDriverWait(driver, TIMEOUT)

    wait.until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(usuario)
    driver.find_element(By.NAME, "password").send_keys(senha)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # TODO: tratar autenticação em dois fatores se necessário
    wait.until(EC.url_contains("fgts.caixa.gov.br/painel"))
    logger.info("Login FGTS concluído")
