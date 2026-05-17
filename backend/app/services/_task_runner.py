"""Utilitário compartilhado para criar tarefas e registrar logs de execução."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.tarefa import Tarefa, TarefaCreate, StatusTarefa
from app.models.log_execucao import LogExecucao
from app.database import SessionLocal


def criar_tarefa(db: Session, data: TarefaCreate) -> Tarefa:
    tarefa = Tarefa(
        empresa_id=data.empresa_id,
        tipo=data.tipo.value,
        status=StatusTarefa.PENDENTE.value,
        parametros=data.parametros,
    )
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


def registrar_log(tarefa_id: int, nivel: str, mensagem: str) -> None:
    db = SessionLocal()
    try:
        log = LogExecucao(tarefa_id=tarefa_id, nivel=nivel, mensagem=mensagem)
        db.add(log)
        db.commit()
    finally:
        db.close()


def atualizar_status(tarefa_id: int, status: StatusTarefa, resultado: dict | None = None) -> None:
    db = SessionLocal()
    try:
        tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
        if tarefa:
            tarefa.status = status.value
            tarefa.atualizado_em = datetime.utcnow()
            if resultado is not None:
                tarefa.resultado = resultado
            db.commit()
    finally:
        db.close()
