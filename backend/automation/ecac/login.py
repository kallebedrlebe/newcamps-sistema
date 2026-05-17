"""Login no portal e-CAC da Receita Federal via Selenium."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

ECAC_URL = "https://cav.receita.fazenda.gov.br/autenticacao/login"
TIMEOUT = 30


def login_certificado(driver, cert_path: str) -> None:
    """Login com certificado digital A1/A3 — requer configuração de proxy de certificado."""
    logger.info("Iniciando login e-CAC via certificado")
    driver.get(ECAC_URL)
    # TODO: implementar fluxo de seleção de certificado
    # O certificado A1 é selecionado pelo browser; A3 via token físico.
    WebDriverWait(driver, TIMEOUT).until(
        EC.url_contains("cav.receita.fazenda.gov.br/aplicacoes")
    )
    logger.info("Login e-CAC concluído")


def login_govbr(driver, cpf: str, senha: str) -> None:
    """Login via gov.br (CPF + senha)."""
    logger.info("Iniciando login e-CAC via gov.br")
    driver.get(ECAC_URL)
    wait = WebDriverWait(driver, TIMEOUT)

    btn_govbr = wait.until(EC.element_to_be_clickable((By.ID, "btnGovBr")))
    btn_govbr.click()

    wait.until(EC.presence_of_element_located((By.ID, "accountId")))
    driver.find_element(By.ID, "accountId").send_keys(cpf)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.presence_of_element_located((By.ID, "password")))
    driver.find_element(By.ID, "password").send_keys(senha)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.url_contains("cav.receita.fazenda.gov.br"))
    logger.info("Login e-CAC via gov.br concluído")
