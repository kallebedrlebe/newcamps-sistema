"""Login no portal e-CAC via gov.br (CPF + senha + 2FA opcional)."""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

ECAC_URL = "https://cav.receita.fazenda.gov.br/autenticacao/login"
GOVBR_URL = "https://accounts.acesso.gov.br"
TIMEOUT = 30
TIMEOUT_2FA = 120  # aguarda até 2 minutos para o operador resolver o 2FA


class LoginEcacError(Exception):
    pass


class MFARequiredError(LoginEcacError):
    """Levantada quando o gov.br exige 2FA e nenhum código foi fornecido."""
    pass


def login_govbr(driver, cpf: str, senha: str, codigo_mfa: str | None = None) -> None:
    """
    Realiza login no e-CAC via gov.br.

    Fluxo:
      1. e-CAC → botão "Entrar com gov.br"
      2. gov.br: digita CPF → Continuar
      3. gov.br: digita senha → Entrar
      4. Se 2FA aparecer: usa codigo_mfa (se fornecido) ou aguarda TIMEOUT_2FA
      5. Valida redirecionamento de volta para e-CAC
    """
    logger.info(f"Iniciando login e-CAC via gov.br (CPF: ***{cpf[-3:]})")
    driver.get(ECAC_URL)
    wait = WebDriverWait(driver, TIMEOUT)

    # ── Passo 1: clica em "Entrar com gov.br" ──────────────────────────────
    try:
        btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[href*='govbr'], button[id*='govbr'], a[id*='govbr'], #btnEntrar")
        ))
        btn.click()
    except TimeoutException:
        # Alguns ambientes redirecionam direto para o gov.br
        if GOVBR_URL not in driver.current_url:
            driver.get(f"{ECAC_URL}?origem=portal")
        logger.debug("Botão gov.br não encontrado, tentando navegação direta")

    # ── Passo 2: aguarda tela do gov.br e digita CPF ──────────────────────
    try:
        wait.until(EC.url_contains("acesso.gov.br"))
    except TimeoutException:
        raise LoginEcacError(f"gov.br não carregou. URL atual: {driver.current_url}")

    wait_govbr = WebDriverWait(driver, TIMEOUT)

    cpf_input = wait_govbr.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#accountId, input[name='cpf'], input[type='text']"))
    )
    cpf_input.clear()
    cpf_input.send_keys(cpf)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #submit-button").click()
    logger.debug("CPF enviado")

    # ── Passo 3: digita senha ──────────────────────────────────────────────
    senha_input = wait_govbr.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#password, input[type='password']"))
    )
    senha_input.clear()
    senha_input.send_keys(senha)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #submit-button").click()
    logger.debug("Senha enviada")

    # ── Passo 4: detecta e resolve 2FA ────────────────────────────────────
    try:
        mfa_detected = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "input[name='code'], input[name='otp'], #totp-input, .mfa-input"
            ))
        )
        logger.info("2FA detectado")

        if codigo_mfa:
            mfa_detected.clear()
            mfa_detected.send_keys(codigo_mfa)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            logger.info("Código 2FA enviado")
        else:
            # Aguarda operador resolver manualmente (útil em modo não-headless)
            logger.warning(f"2FA necessário. Aguardando operador por até {TIMEOUT_2FA}s...")
            WebDriverWait(driver, TIMEOUT_2FA).until(
                EC.url_contains("cav.receita.fazenda.gov.br")
            )
    except TimeoutException:
        # 2FA não apareceu — segue normalmente
        pass

    # ── Passo 5: confirma redirecionamento para e-CAC ─────────────────────
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.url_contains("cav.receita.fazenda.gov.br")
        )
    except TimeoutException:
        raise LoginEcacError(
            f"Não redirecionou para o e-CAC após login. URL: {driver.current_url}"
        )

    # Verifica se há mensagem de erro (credenciais inválidas)
    try:
        erro = driver.find_element(By.CSS_SELECTOR, ".alert-danger, .error-message, #error-message")
        raise LoginEcacError(f"Erro de autenticação: {erro.text.strip()}")
    except NoSuchElementException:
        pass

    logger.info("Login e-CAC concluído com sucesso")


def login_certificado(driver, cert_path: str) -> None:
    """Login com certificado digital A1 — o browser seleciona o cert automaticamente."""
    logger.info("Iniciando login e-CAC via certificado digital")
    driver.get(ECAC_URL)
    wait = WebDriverWait(driver, TIMEOUT)

    btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#btnCertificado, a[href*='certificado']")
    ))
    btn.click()

    WebDriverWait(driver, TIMEOUT).until(
        EC.url_contains("cav.receita.fazenda.gov.br/aplicacoes")
    )
    logger.info("Login via certificado concluído")
