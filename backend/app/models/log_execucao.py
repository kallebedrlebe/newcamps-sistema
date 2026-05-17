from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel
from app.database import Base


class LogExecucao(Base):
    __tablename__ = "logs_execucao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tarefa_id: Mapped[int] = mapped_column(sa.ForeignKey("tarefas.id"), index=True)
    nivel: Mapped[str] = mapped_column(sa.String(10))  # INFO | WARN | ERROR
    mensagem: Mapped[str] = mapped_column(sa.Text)
    ts: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())

    tarefa: Mapped["Tarefa"] = relationship("Tarefa", back_populates="logs")  # noqa: F821


# ---------- Schema Pydantic ----------

class LogRead(BaseModel):
    id: int
    tarefa_id: int
    nivel: str
    mensagem: str
    ts: datetime

    model_config = {"from_attributes": True}
