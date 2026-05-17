from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tarefa import TarefaCreate, TarefaRead, TipoTarefa
from app.services.fgts_service import enfileirar_tarefa_fgts

router = APIRouter()


@router.post("/saldo", response_model=TarefaRead, status_code=202)
def consultar_saldo(
    empresa_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(empresa_id=empresa_id, tipo=TipoTarefa.FGTS_SALDO)
    return enfileirar_tarefa_fgts(db, bg, payload)


@router.post("/extrato", response_model=TarefaRead, status_code=202)
def obter_extrato(
    empresa_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(empresa_id=empresa_id, tipo=TipoTarefa.FGTS_EXTRATO)
    return enfileirar_tarefa_fgts(db, bg, payload)
