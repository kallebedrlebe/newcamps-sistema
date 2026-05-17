"""Login no sistema TRON."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

TIMEOUT = 30


def login_tron(driver, url: str, usuario: str, senha: str) -> None:
    logger.info(f"Iniciando login TRON: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, TIMEOUT)

    wait.until(EC.presence_of_element_located((By.NAME, "usuario")))
    driver.find_element(By.NAME, "usuario").send_keys(usuario)
    driver.find_element(By.NAME, "senha").send_keys(senha)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

    # TODO: ajustar seletor e URL de destino conforme instância TRON
    wait.until(lambda d: "login" not in d.current_url.lower())
    logger.info("Login TRON concluído")
