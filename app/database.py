#serve para criar conexão com o postgres e disponibilizar a sessão do banco para o resto do projeto.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#abre a porta do banco, empresta a chave, assim que o usuário devolver a chave ele fecha a porta.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        