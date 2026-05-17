from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tarefa import TarefaCreate, TarefaRead, TipoTarefa
from app.services.tron_service import enfileirar_tarefa_tron

router = APIRouter()


@router.post("/processar", response_model=TarefaRead, status_code=202)
def processar(
    empresa_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(empresa_id=empresa_id, tipo=TipoTarefa.TRON_PROCESSAMENTO)
    return enfileirar_tarefa_tron(db, bg, payload)


@router.post("/relatorio", response_model=TarefaRead, status_code=202)
def gerar_relatorio(
    empresa_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    payload = TarefaCreate(empresa_id=empresa_id, tipo=TipoTarefa.TRON_RELATORIO)
    return enfileirar_tarefa_tron(db, bg, payload)
