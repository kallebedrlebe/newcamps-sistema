from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.dependencies import get_db, get_current_user
from app.models.tarefa import TarefaCreate, TarefaRead, TipoTarefa
from app.services.ecac_service import enfileirar_tarefa_ecac, enfileirar_dctfweb_esocial

router = APIRouter()


class DctfWebRequest(BaseModel):
    empresa_id: int
    competencia: str   # MM/AAAA — ex: "01/2024"
    codigo_mfa: str | None = None


@router.post("/dctfweb/esocial", response_model=TarefaRead, status_code=202, summary="DCTFWeb — emite DARF eSocial")
def dctfweb_esocial(
    body: DctfWebRequest,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Acessa a DCTFWeb no e-CAC e emite o DARF do eSocial para a competência informada.

    - **empresa_id**: ID da empresa (credenciais govbr_cpf / govbr_senha em `credenciais`)
    - **competencia**: MM/AAAA (ex: `01/2024`)
    - **codigo_mfa**: código 2FA do gov.br, se a conta utilizar autenticação em dois fatores
    """
    _validar_competencia(body.competencia)
    return enfileirar_dctfweb_esocial(db, bg, body.empresa_id, body.competencia, body.codigo_mfa)


@router.post("/darf", response_model=TarefaRead, status_code=202)
def emitir_darf(
    empresa_id: int,
    competencia: str,
    codigo_receita: str,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(
        empresa_id=empresa_id,
        tipo=TipoTarefa.ECAC_DARF,
        parametros={"competencia": competencia, "codigo_receita": codigo_receita},
    )
    return enfileirar_tarefa_ecac(db, bg, payload)


@router.post("/debitos", response_model=TarefaRead, status_code=202)
def consultar_debitos(
    empresa_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(empresa_id=empresa_id, tipo=TipoTarefa.ECAC_DEBITOS)
    return enfileirar_tarefa_ecac(db, bg, payload)


@router.post("/parcelamento", response_model=TarefaRead, status_code=202)
def solicitar_parcelamento(
    empresa_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(empresa_id=empresa_id, tipo=TipoTarefa.ECAC_PARCELAMENTO)
    return enfileirar_tarefa_ecac(db, bg, payload)


def _validar_competencia(competencia: str) -> None:
    import re
    if not re.fullmatch(r"\d{2}/\d{4}", competencia):
        raise HTTPException(status_code=422, detail="competencia deve estar no formato MM/AAAA")
    mes, ano = int(competencia[:2]), int(competencia[3:])
    if not (1 <= mes <= 12):
        raise HTTPException(status_code=422, detail="Mês inválido")
    if ano < 2018:
        raise HTTPException(status_code=422, detail="eSocial iniciou em 2018")
