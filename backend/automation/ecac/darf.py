"""Emissão de DARF no e-CAC."""
from loguru import logger
from automation.utils.browser import criar_driver
from automation.ecac.login import login_govbr
from app.database import SessionLocal
from app.models.empresa import Empresa

DARF_URL = "https://cav.receita.fazenda.gov.br/aplicacoes/atbhe/sicalc-internet/index.html"


def emitir_darf(empresa_id: int, parametros: dict) -> dict:
    db = SessionLocal()
    try:
        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        creds = empresa.credenciais or {}
    finally:
        db.close()

    driver = criar_driver(headless=True)
    try:
        login_govbr(driver, creds.get("govbr_cpf", ""), creds.get("govbr_senha", ""))
        driver.get(DARF_URL)

        competencia = parametros.get("competencia", "")
        codigo_receita = parametros.get("codigo_receita", "")

        # TODO: preencher formulário DARF com competencia e codigo_receita
        logger.info(f"Emitindo DARF: empresa={empresa_id} comp={competencia} cod={codigo_receita}")

        return {
            "status": "emitido",
            "competencia": competencia,
            "codigo_receita": codigo_receita,
            "empresa_id": empresa_id,
        }
    finally:
        driver.quit()
