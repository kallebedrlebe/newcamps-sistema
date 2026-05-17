from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tarefa import TarefaCreate, TarefaRead, TipoTarefa
from app.services.ecac_service import enfileirar_tarefa_ecac

router = APIRouter()


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
