"""Processamento de transações no TRON."""
from loguru import logger
from automation.utils.browser import criar_driver
from automation.tron.login import login_tron
from app.database import SessionLocal
from app.models.empresa import Empresa


def processar(empresa_id: int, parametros: dict) -> dict:
    db = SessionLocal()
    try:
        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        creds = empresa.credenciais or {}
    finally:
        db.close()

    driver = criar_driver(headless=True)
    try:
        login_tron(
            driver,
            creds.get("tron_url", ""),
            creds.get("tron_user", ""),
            creds.get("tron_pass", ""),
        )

        # TODO: executar fluxo de processamento específico
        logger.info(f"Processando TRON: empresa={empresa_id} params={parametros}")

        return {"empresa_id": empresa_id, "status": "processado", **parametros}
    finally:
        driver.quit()
