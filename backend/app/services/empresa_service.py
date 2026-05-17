from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.empresa import Empresa, EmpresaCreate, EmpresaUpdate


def create_empresa(db: Session, data: EmpresaCreate) -> Empresa:
    emp = Empresa(
        razao_social=data.razao_social,
        cnpj=data.cnpj,
        credenciais=data.credenciais or {},
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def update_empresa(db: Session, empresa_id: int, data: EmpresaUpdate) -> Empresa:
    emp = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    if data.razao_social is not None:
        emp.razao_social = data.razao_social
    if data.credenciais is not None:
        emp.credenciais = data.credenciais
    if data.ativa is not None:
        emp.ativa = data.ativa
    db.commit()
    db.refresh(emp)
    return emp
