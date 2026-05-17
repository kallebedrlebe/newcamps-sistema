from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger
from app.models.tarefa import TarefaCreate, Tarefa, StatusTarefa, TipoTarefa
from app.services._task_runner import criar_tarefa, registrar_log, atualizar_status
from automation.ecac.darf import emitir_darf
from automation.ecac.debitos import consultar_debitos
from automation.ecac.parcelamento import solicitar_parcelamento


def enfileirar_tarefa_ecac(db: Session, bg: BackgroundTasks, data: TarefaCreate) -> Tarefa:
    tarefa = criar_tarefa(db, data)
    bg.add_task(_executar, tarefa.id, data)
    return tarefa


def _executar(tarefa_id: int, data: TarefaCreate) -> None:
    atualizar_status(tarefa_id, StatusTarefa.EM_EXECUCAO)
    registrar_log(tarefa_id, "INFO", f"Iniciando {data.tipo.value}")
    try:
        if data.tipo == TipoTarefa.ECAC_DARF:
            resultado = emitir_darf(data.empresa_id, data.parametros or {})
        elif data.tipo == TipoTarefa.ECAC_DEBITOS:
            resultado = consultar_debitos(data.empresa_id)
        elif data.tipo == TipoTarefa.ECAC_PARCELAMENTO:
            resultado = solicitar_parcelamento(data.empresa_id, data.parametros or {})
        else:
            resultado = {}
        registrar_log(tarefa_id, "INFO", "Concluído com sucesso")
        atualizar_status(tarefa_id, StatusTarefa.CONCLUIDA, resultado)
    except Exception as exc:
        logger.exception(f"Erro na tarefa ECAC {tarefa_id}")
        registrar_log(tarefa_id, "ERROR", str(exc))
        atualizar_status(tarefa_id, StatusTarefa.ERRO)
