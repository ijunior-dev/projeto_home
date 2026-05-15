import os

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import User  # noqa: E402
from app.security import get_password_hash  # noqa: E402


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                email="admin@email.com",
                hashed_password=get_password_hash("123456"),
                is_active=True,
            ))
            db.commit()
            print("Usuário admin criado com sucesso.")
        else:
            print("Usuário admin já existe.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
