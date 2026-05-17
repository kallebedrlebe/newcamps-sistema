from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.empresa import Empresa, EmpresaCreate, EmpresaRead, EmpresaUpdate
from app.services.empresa_service import create_empresa, update_empresa

router = APIRouter()


@router.get("/", response_model=list[EmpresaRead])
def list_empresas(ativa: bool | None = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Empresa)
    if ativa is not None:
        q = q.filter(Empresa.ativa == ativa)
    return q.order_by(Empresa.razao_social).all()


@router.post("/", response_model=EmpresaRead, status_code=status.HTTP_201_CREATED)
def create(body: EmpresaCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    existing = db.query(Empresa).filter(Empresa.cnpj == body.cnpj).first()
    if existing:
        raise HTTPException(status_code=409, detail="CNPJ já cadastrado")
    return create_empresa(db, body)


@router.get("/{empresa_id}", response_model=EmpresaRead)
def get_empresa(empresa_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    emp = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return emp


@router.put("/{empresa_id}", response_model=EmpresaRead)
def update(empresa_id: int, body: EmpresaUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return update_empresa(db, empresa_id, body)


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(empresa_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if not current.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores")
    emp = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    db.delete(emp)
    db.commit()
