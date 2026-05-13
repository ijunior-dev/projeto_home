# Serve para inserir um usuário admin inicial com senha em hash.

from app.database import SessionLocal, engine, Base
from app.models import User
from app.security import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

user_exists = db.query(User).filter(User.username == "admin").first()

if not user_exists:
    new_user = User(
        username="admin",
        email="admin@email.com",
        hashed_password=get_password_hash("123456"),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    print("Usuário admin criado com sucesso.")
else:
    print("Usuário admin já existe.")

db.close()