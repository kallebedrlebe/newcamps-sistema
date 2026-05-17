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


def enfileirar_dctfweb_esocial(
    db: Session,
    bg: BackgroundTasks,
    empresa_id: int,
    competencia: str,
    codigo_mfa: str | None,
) -> Tarefa:
    data = TarefaCreate(
        empresa_id=empresa_id,
        tipo=TipoTarefa.ECAC_DCTFWEB_ESOCIAL,
        parametros={"competencia": competencia, "codigo_mfa": codigo_mfa},
    )
    tarefa = criar_tarefa(db, data)
    bg.add_task(_executar_dctfweb, tarefa.id, empresa_id, competencia, codigo_mfa)
    return tarefa


# ── Executores em background ────────────────────────────────────────────────

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


def _executar_dctfweb(
    tarefa_id: int,
    empresa_id: int,
    competencia: str,
    codigo_mfa: str | None,
) -> None:
    from automation.utils.browser import criar_driver
    from automation.ecac.login import login_govbr, LoginEcacError
    from automation.ecac.dctfweb import emitir_darf_esocial, DctfWebError
    from app.database import SessionLocal
    from app.models.empresa import Empresa

    atualizar_status(tarefa_id, StatusTarefa.EM_EXECUCAO)
    registrar_log(tarefa_id, "INFO", f"DCTFWeb eSocial | competência {competencia}")

    db = SessionLocal()
    try:
        empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
        if not empresa:
            raise ValueError(f"Empresa {empresa_id} não encontrada")
        creds = empresa.credenciais or {}
        cnpj = empresa.cnpj
    finally:
        db.close()

    cpf = creds.get("govbr_cpf", "")
    senha = creds.get("govbr_senha", "")
    if not cpf or not senha:
        registrar_log(tarefa_id, "ERROR", "Credenciais gov.br não configuradas para esta empresa")
        atualizar_status(tarefa_id, StatusTarefa.ERRO)
        return

    driver = criar_driver(headless=True)
    try:
        registrar_log(tarefa_id, "INFO", "Realizando login no e-CAC via gov.br")
        login_govbr(driver, cpf, senha, codigo_mfa)

        registrar_log(tarefa_id, "INFO", "Login OK — acessando DCTFWeb")
        resultado = emitir_darf_esocial(driver, competencia, cnpj)

        registrar_log(
            tarefa_id, "INFO",
            f"DARF emitido: R$ {resultado.get('valor_total', '?')} | "
            f"venc {resultado.get('data_vencimento', '?')} | "
            f"receita {resultado.get('codigo_receita', '?')}"
        )
        atualizar_status(tarefa_id, StatusTarefa.CONCLUIDA, resultado)

    except (LoginEcacError, DctfWebError) as exc:
        logger.warning(f"Erro DCTFWeb tarefa {tarefa_id}: {exc}")
        registrar_log(tarefa_id, "ERROR", str(exc))
        atualizar_status(tarefa_id, StatusTarefa.ERRO)
    except Exception as exc:
        logger.exception(f"Erro inesperado DCTFWeb tarefa {tarefa_id}")
        registrar_log(tarefa_id, "ERROR", f"Erro inesperado: {exc}")
        atualizar_status(tarefa_id, StatusTarefa.ERRO)
    finally:
        driver.quit()
