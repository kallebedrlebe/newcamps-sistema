from datetime import datetime
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, field_validator
from app.database import Base


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    razao_social: Mapped[str] = mapped_column(sa.String(200))
    cnpj: Mapped[str] = mapped_column(sa.String(14), unique=True, index=True)
    credenciais: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)
    ativa: Mapped[bool] = mapped_column(sa.Boolean, default=True, server_default=sa.true())
    criado_em: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())

    tarefas: Mapped[list["Tarefa"]] = relationship("Tarefa", back_populates="empresa")  # noqa: F821


# ---------- Schemas Pydantic ----------

class EmpresaCreate(BaseModel):
    razao_social: str
    cnpj: str
    credenciais: Optional[dict] = None

    @field_validator("cnpj")
    @classmethod
    def cnpj_apenas_digitos(cls, v: str) -> str:
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")
        return digits


class EmpresaRead(BaseModel):
    id: int
    razao_social: str
    cnpj: str
    ativa: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class EmpresaUpdate(BaseModel):
    razao_social: Optional[str] = None
    credenciais: Optional[dict] = None
    ativa: Optional[bool] = None
