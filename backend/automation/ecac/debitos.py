"""Consulta de débitos no e-CAC."""
from loguru import logger
from automation.utils.browser import criar_driver
from automation.ecac.login import login_govbr
from app.database import SessionLocal
from app.models.empresa import Empresa

DEBITOS_URL = "https://cav.receita.fazenda.gov.br/aplicacoes/atbhe/debitosEfd/index.html"


def consultar_debitos(empresa_id: int) -> dict:
    db = SessionLocal()
    try:
        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        creds = empresa.credenciais or {}
    finally:
        db.close()

    driver = criar_driver(headless=True)
    try:
        login_govbr(driver, creds.get("govbr_cpf", ""), creds.get("govbr_senha", ""))
        driver.get(DEBITOS_URL)

        # TODO: extrair tabela de débitos da página
        logger.info(f"Consultando débitos: empresa={empresa_id}")

        return {"empresa_id": empresa_id, "debitos": []}
    finally:
        driver.quit()
