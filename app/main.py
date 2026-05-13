#serve para subir a aplicação FastAPI principal

from fastapi import Depends, FastAPI

from app.auth import get_current_user, router as auth_router
from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Projeto Fase 8")

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/protegida")
def rota_protegida(usuario=Depends(get_current_user)):
    return {"mensagem": f"Olá, {usuario}. Sua rota protegida está funcionando."}

