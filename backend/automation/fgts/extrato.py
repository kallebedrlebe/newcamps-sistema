"""Extrato FGTS por competência."""
from loguru import logger
from automation.utils.browser import criar_driver
from automation.fgts.login import login_fgts
from app.database import SessionLocal
from app.models.empresa import Empresa


def obter_extrato(empresa_id: int) -> dict:
    db = SessionLocal()
    try:
        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        creds = empresa.credenciais or {}
    finally:
        db.close()

    driver = criar_driver(headless=True)
    try:
        login_fgts(driver, creds.get("fgts_user", ""), creds.get("fgts_pass", ""))

        # TODO: navegar até extrato e retornar linhas
        logger.info(f"Obtendo extrato FGTS: empresa={empresa_id}")

        return {"empresa_id": empresa_id, "competencias": []}
    finally:
        driver.quit()
