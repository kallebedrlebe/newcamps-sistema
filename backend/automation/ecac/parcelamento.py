"""Solicitação de parcelamento de débitos no e-CAC."""
from loguru import logger
from automation.utils.browser import criar_driver
from automation.ecac.login import login_govbr
from app.database import SessionLocal
from app.models.empresa import Empresa

PARCELAMENTO_URL = "https://cav.receita.fazenda.gov.br/aplicacoes/atbhe/parcelamento/index.html"


def solicitar_parcelamento(empresa_id: int, parametros: dict) -> dict:
    db = SessionLocal()
    try:
        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        creds = empresa.credenciais or {}
    finally:
        db.close()

    driver = criar_driver(headless=True)
    try:
        login_govbr(driver, creds.get("govbr_cpf", ""), creds.get("govbr_senha", ""))
        driver.get(PARCELAMENTO_URL)

        # TODO: preencher e submeter formulário de parcelamento
        logger.info(f"Solicitando parcelamento: empresa={empresa_id}")

        return {"empresa_id": empresa_id, "status": "solicitado", **parametros}
    finally:
        driver.quit()
