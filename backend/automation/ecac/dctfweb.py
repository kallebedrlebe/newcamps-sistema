"""
DCTFWeb — emissão de DARF do eSocial via e-CAC.

Fluxo:
  1. Login no e-CAC (via login.py)
  2. Navega para a DCTFWeb
  3. Filtra pela competência informada (MM/AAAA)
  4. Localiza a linha do eSocial na tabela de declarações
  5. Clica em "Emitir DARF"
  6. Extrai: valor, vencimento, código de barras, nosso número
  7. Retorna dict com os dados do DARF
"""
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger

DCTFWEB_URL = "https://cav.receita.fazenda.gov.br/aplicacoes/AEAT/DCTFWeb/"
TIMEOUT = 30
TIMEOUT_DARF = 60  # DCTFWeb pode demorar para carregar o DARF


class DctfWebError(Exception):
    pass


# Códigos de receita do eSocial na DCTFWeb
CODIGOS_ESOCIAL = {
    "2484",  # INSS — Contribuições Previdenciárias eSocial
    "2500",  # IRRF — Rendimentos do Trabalho eSocial
    "2507",  # IRRF — Outras Retenções eSocial
}


def emitir_darf_esocial(driver, competencia: str, cnpj: str) -> dict:
    """
    Navega para a DCTFWeb e emite o DARF do eSocial para a competência informada.

    Args:
        driver: WebDriver autenticado no e-CAC.
        competencia: Competência no formato MM/AAAA (ex: "01/2024").
        cnpj: CNPJ da empresa (14 dígitos, sem máscara).

    Returns:
        Dict com dados do DARF: valor_total, data_vencimento, codigo_barras,
        nosso_numero, competencia, codigo_receita, pdf_url.

    Raises:
        DctfWebError: se não encontrar declaração ou DARF para a competência.
    """
    logger.info(f"DCTFWeb | CNPJ: {cnpj[:8]}*** | Competência: {competencia}")

    driver.get(DCTFWEB_URL)
    wait = WebDriverWait(driver, TIMEOUT)

    # ── Aguarda carregamento inicial da DCTFWeb ─────────────────────────────
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".dctfweb-container, #main-content, table, .grid-container")
        ))
    except TimeoutException:
        raise DctfWebError(f"DCTFWeb não carregou. URL: {driver.current_url}")

    time.sleep(2)  # aguarda renderização completa do SPA

    # ── Seleciona/filtra pela competência ──────────────────────────────────
    _selecionar_competencia(driver, wait, competencia)

    # ── Localiza a linha do eSocial na tabela ──────────────────────────────
    linha = _localizar_linha_esocial(driver, wait)
    if not linha:
        raise DctfWebError(
            f"Nenhuma declaração eSocial encontrada para competência {competencia}. "
            "Verifique se a DCTFWeb foi transmitida."
        )

    # ── Clica em "Emitir DARF" ─────────────────────────────────────────────
    logger.info("Clicando em Emitir DARF")
    _clicar_emitir_darf(driver, linha)

    # ── Extrai dados do DARF ───────────────────────────────────────────────
    dados = _extrair_dados_darf(driver)
    dados.update({
        "competencia": competencia,
        "cnpj": cnpj,
        "origem": "DCTFWEB_ESOCIAL",
    })

    logger.info(
        f"DARF emitido | Receita: {dados.get('codigo_receita')} "
        f"| Valor: R$ {dados.get('valor_total')} "
        f"| Venc: {dados.get('data_vencimento')}"
    )
    return dados


# ── Funções auxiliares ──────────────────────────────────────────────────────

def _selecionar_competencia(driver, wait: WebDriverWait, competencia: str) -> None:
    """Preenche o filtro de competência na DCTFWeb (MM/AAAA)."""
    # Tenta via input de texto (campo de filtro)
    try:
        filtro = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "input[placeholder*='competência'], input[placeholder*='Competência'], "
            "input[name*='competencia'], input[id*='competencia']"
        )))
        filtro.clear()
        filtro.send_keys(competencia)
        # Botão buscar
        try:
            driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .btn-buscar, #btn-pesquisar").click()
        except NoSuchElementException:
            from selenium.webdriver.common.keys import Keys
            filtro.send_keys(Keys.ENTER)
        time.sleep(2)
        logger.debug(f"Competência filtrada: {competencia}")
        return
    except TimeoutException:
        pass

    # Tenta via dropdown Select
    try:
        select_el = driver.find_element(By.CSS_SELECTOR, "select[name*='competencia'], select[id*='competencia']")
        Select(select_el).select_by_visible_text(competencia)
        time.sleep(2)
        return
    except NoSuchElementException:
        pass

    logger.warning("Campo de filtro de competência não encontrado — usando listagem completa")


def _localizar_linha_esocial(driver, wait: WebDriverWait):
    """
    Procura na tabela da DCTFWeb a linha correspondente ao eSocial.
    Retorna o elemento <tr> ou None.
    """
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr, .grid-row")))
    except TimeoutException:
        return None

    linhas = driver.find_elements(By.CSS_SELECTOR, "table tbody tr, .grid-row")
    logger.debug(f"Linhas na tabela DCTFWeb: {len(linhas)}")

    for linha in linhas:
        texto = linha.text.upper()
        # Detecta eSocial por texto ou código de receita
        if "ESOCIAL" in texto or "E-SOCIAL" in texto:
            logger.debug(f"Linha eSocial encontrada: {linha.text[:80]}")
            return linha
        for cod in CODIGOS_ESOCIAL:
            if cod in texto:
                logger.debug(f"Linha eSocial por código {cod}: {linha.text[:80]}")
                return linha

    return None


def _clicar_emitir_darf(driver, linha) -> None:
    """Clica no botão 'Emitir DARF' ou 'Gerar DARF' dentro da linha encontrada."""
    seletores_btn = [
        "button[title*='DARF'], button[title*='Darf']",
        "a[title*='DARF'], a[title*='Darf']",
        "button:contains('DARF'), button:contains('Emitir')",
        ".btn-darf, .emitir-darf",
    ]
    # Tenta dentro da linha
    for seletor in seletores_btn:
        try:
            btn = linha.find_element(By.CSS_SELECTOR, seletor)
            btn.click()
            return
        except NoSuchElementException:
            pass

    # Tenta por texto dentro da linha
    try:
        btns = linha.find_elements(By.TAG_NAME, "button") + linha.find_elements(By.TAG_NAME, "a")
        for btn in btns:
            if "DARF" in btn.text.upper() or "EMITIR" in btn.text.upper():
                btn.click()
                return
    except Exception:
        pass

    raise DctfWebError("Botão 'Emitir DARF' não encontrado na linha do eSocial.")


def _extrair_dados_darf(driver) -> dict:
    """
    Extrai os dados do DARF após clicar em Emitir.
    Suporta: nova aba, modal ou página inline.
    """
    wait = WebDriverWait(driver, TIMEOUT_DARF)

    # Se abriu nova aba, muda o foco
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        logger.debug("Trocou para nova aba do DARF")

    # Aguarda carregamento do DARF (busca campos-chave)
    try:
        wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            ".darf-container, #darf, .valor-total, table.darf, iframe"
        )))
    except TimeoutException:
        pass  # Tenta extrair mesmo assim

    time.sleep(2)

    # Se o DARF está em um iframe, entra nele
    try:
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe[src*='darf'], iframe[name*='darf']")
        driver.switch_to.frame(iframe)
        logger.debug("Entrou no iframe do DARF")
    except NoSuchElementException:
        pass

    page_text = driver.find_element(By.TAG_NAME, "body").text

    dados = {
        "codigo_receita": _extrair_regex(page_text, r"C[oó]digo\s*(?:da\s*)?Receita[:\s]+(\d{4})", ""),
        "valor_principal": _extrair_valor(page_text, r"Valor\s*(?:do\s*)?Principal[:\s]+([\d.,]+)"),
        "valor_multa": _extrair_valor(page_text, r"Multa[:\s]+([\d.,]+)"),
        "valor_juros": _extrair_valor(page_text, r"Juros[:\s]+([\d.,]+)"),
        "valor_total": _extrair_valor(page_text, r"Valor\s*Total[:\s]+([\d.,]+)") or
                       _extrair_valor(page_text, r"Total\s*a\s*(?:Pagar|Recolher)[:\s]+([\d.,]+)"),
        "data_vencimento": _extrair_regex(page_text, r"(?:Data\s*de\s*)?Vencimento[:\s]+(\d{2}/\d{2}/\d{4})", ""),
        "nosso_numero": _extrair_regex(page_text, r"Nosso\s*N[uú]mero[:\s]+([\d\s]+)", "").strip(),
        "codigo_barras": _extrair_codigo_barras(page_text),
        "pdf_url": driver.current_url,
    }

    # Fallback: tenta por campos HTML específicos
    dados = _enriquecer_por_html(driver, dados)

    return dados


def _enriquecer_por_html(driver, dados: dict) -> dict:
    """Complementa extração lendo elementos HTML diretamente."""
    mapa = {
        "codigo_receita": ["#codigoReceita", ".codigo-receita", "td.codigo"],
        "valor_total": ["#valorTotal", ".valor-total", "#totalPagar", ".total-recolher"],
        "data_vencimento": ["#dataVencimento", ".data-vencimento", "#vencimento"],
        "nosso_numero": ["#nossoNumero", ".nosso-numero"],
        "codigo_barras": ["#codigoBarras", ".codigo-barras", "#linhaDigitavel"],
    }
    for campo, seletores in mapa.items():
        if dados.get(campo):
            continue
        for seletor in seletores:
            try:
                el = driver.find_element(By.CSS_SELECTOR, seletor)
                valor = el.text.strip() or el.get_attribute("value", "").strip()
                if valor:
                    dados[campo] = valor
                    break
            except NoSuchElementException:
                pass
    return dados


def _extrair_regex(texto: str, padrao: str, default: str) -> str:
    m = re.search(padrao, texto, re.IGNORECASE)
    return m.group(1).strip() if m else default


def _extrair_valor(texto: str, padrao: str) -> float | None:
    m = re.search(padrao, texto, re.IGNORECASE)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _extrair_codigo_barras(texto: str) -> str:
    # Linha digitável: blocos de dígitos separados por espaço ou ponto
    m = re.search(r"(\d{5}\.\d{5}\s+\d{5}\.\d{6}\s+\d{5}\.\d{6}\s+\d\s+\d{14})", texto)
    if m:
        return m.group(1).strip()
    # Código de barras numérico puro (44 dígitos)
    m = re.search(r"\b(\d{44})\b", texto)
    return m.group(1) if m else ""
