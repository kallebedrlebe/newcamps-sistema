from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger
from app.models.tarefa import TarefaCreate, Tarefa, StatusTarefa, TipoTarefa
from app.services._task_runner import criar_tarefa, registrar_log, atualizar_status
from automation.tron.processamento import processar
from automation.tron.relatorio import gerar_relatorio


def enfileirar_tarefa_tron(db: Session, bg: BackgroundTasks, data: TarefaCreate) -> Tarefa:
    tarefa = criar_tarefa(db, data)
    bg.add_task(_executar, tarefa.id, data)
    return tarefa


def _executar(tarefa_id: int, data: TarefaCreate) -> None:
    atualizar_status(tarefa_id, StatusTarefa.EM_EXECUCAO)
    registrar_log(tarefa_id, "INFO", f"Iniciando {data.tipo.value}")
    try:
        if data.tipo == TipoTarefa.TRON_PROCESSAMENTO:
            resultado = processar(data.empresa_id, data.parametros or {})
        elif data.tipo == TipoTarefa.TRON_RELATORIO:
            resultado = gerar_relatorio(data.empresa_id)
        else:
            resultado = {}
        registrar_log(tarefa_id, "INFO", "Concluído com sucesso")
        atualizar_status(tarefa_id, StatusTarefa.CONCLUIDA, resultado)
    except Exception as exc:
        logger.exception(f"Erro na tarefa TRON {tarefa_id}")
        registrar_log(tarefa_id, "ERROR", str(exc))
        atualizar_status(tarefa_id, StatusTarefa.ERRO)
