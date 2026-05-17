from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User, UserCreate, UserUpdate
from app.services.auth_service import hash_password


def create_user(db: Session, data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    user = User(
        nome=data.nome,
        email=data.email,
        senha_hash=hash_password(data.senha),
        is_admin=data.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if data.nome is not None:
        user.nome = data.nome
    if data.email is not None:
        user.email = data.email
    if data.senha is not None:
        user.senha_hash = hash_password(data.senha)
    db.commit()
    db.refresh(user)
    return user
