from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User, UserCreate, UserRead, UserUpdate
from app.services.user_service import create_user, update_user

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(User).all()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create(body: UserCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if not current.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar usuários")
    return create_user(db, body)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update(user_id: int, body: UserUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if not current.is_admin and current.id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    return update_user(db, user_id, body)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if not current.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(user)
    db.commit()
