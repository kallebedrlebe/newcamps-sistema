"""Geração de relatório no TRON."""
from loguru import logger
from automation.utils.browser import criar_driver
from automation.tron.login import login_tron
from app.database import SessionLocal
from app.models.empresa import Empresa


def gerar_relatorio(empresa_id: int) -> dict:
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

        # TODO: navegar até relatório, exportar e retornar dados
        logger.info(f"Gerando relatório TRON: empresa={empresa_id}")

        return {"empresa_id": empresa_id, "relatorio": None}
    finally:
        driver.quit()
