#Centraliza a busca de usuário no banco e a validação do login.abs

from sqlalchemy.orm import Session
from app.models import User
from app.security import verify_password


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user