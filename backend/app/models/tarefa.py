import enum
from datetime import datetime
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from app.database import Base


class TipoTarefa(str, enum.Enum):
    ECAC_DARF = "ECAC_DARF"
    ECAC_DEBITOS = "ECAC_DEBITOS"
    ECAC_PARCELAMENTO = "ECAC_PARCELAMENTO"
    ECAC_DCTFWEB_ESOCIAL = "ECAC_DCTFWEB_ESOCIAL"   # DCTFWeb → DARF eSocial
    FGTS_SALDO = "FGTS_SALDO"
    FGTS_EXTRATO = "FGTS_EXTRATO"
    TRON_PROCESSAMENTO = "TRON_PROCESSAMENTO"
    TRON_RELATORIO = "TRON_RELATORIO"


class StatusTarefa(str, enum.Enum):
    PENDENTE = "PENDENTE"
    EM_EXECUCAO = "EM_EXECUCAO"
    CONCLUIDA = "CONCLUIDA"
    ERRO = "ERRO"


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    empresa_id: Mapped[int] = mapped_column(sa.ForeignKey("empresas.id"), index=True)
    tipo: Mapped[str] = mapped_column(sa.String(40))
    status: Mapped[str] = mapped_column(sa.String(20), default=StatusTarefa.PENDENTE, server_default="PENDENTE")
    parametros: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)
    resultado: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()
    )

    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="tarefas")  # noqa: F821
    logs: Mapped[list["LogExecucao"]] = relationship("LogExecucao", back_populates="tarefa", cascade="all, delete-orphan")  # noqa: F821


# ---------- Schemas Pydantic ----------

class TarefaCreate(BaseModel):
    empresa_id: int
    tipo: TipoTarefa
    parametros: Optional[dict] = None


class TarefaRead(BaseModel):
    id: int
    empresa_id: int
    tipo: str
    status: str
    parametros: Optional[dict]
    resultado: Optional[dict]
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}
