from datetime import datetime
from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, EmailStr
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(sa.String(120))
    email: Mapped[str] = mapped_column(sa.String(254), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(sa.String(255))
    is_admin: Mapped[bool] = mapped_column(sa.Boolean, default=False, server_default=sa.false())
    criado_em: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())


# ---------- Schemas Pydantic ----------

class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    is_admin: bool = False


class UserRead(BaseModel):
    id: int
    nome: str
    email: str
    is_admin: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
