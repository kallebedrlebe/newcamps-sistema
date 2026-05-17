from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.tarefa import Tarefa, TarefaRead
from app.models.log_execucao import LogRead

router = APIRouter()


@router.get("/", response_model=list[TarefaRead])
def list_tarefas(
    empresa_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Tarefa)
    if empresa_id:
        q = q.filter(Tarefa.empresa_id == empresa_id)
    if status:
        q = q.filter(Tarefa.status == status)
    return q.order_by(Tarefa.criado_em.desc()).limit(200).all()


@router.get("/{tarefa_id}", response_model=TarefaRead)
def get_tarefa(tarefa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return t


@router.get("/{tarefa_id}/logs", response_model=list[LogRead])
def get_logs(tarefa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    from app.models.log_execucao import LogExecucao
    return db.query(LogExecucao).filter(LogExecucao.tarefa_id == tarefa_id).order_by(LogExecucao.ts).all()
