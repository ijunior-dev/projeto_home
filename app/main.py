import logging
import os
import socket as _socket

import httpx
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models  # noqa: F401 — registra modelos no SQLAlchemy
from app.auth import get_current_user, router as auth_router
from app.database import get_db
from app.limiter import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Projeto Fase 8")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status")
def system_status(db: Session = Depends(get_db)):
    result = {
        "api": "online",
        "database": "unknown",
        "supabase": "unknown",
        "tcp_server": "unknown",
    }

    try:
        db.execute(text("SELECT 1"))
        result["database"] = "online"
    except Exception:
        result["database"] = "offline"

    try:
        r = httpx.get("http://127.0.0.1:54321/health", timeout=2.0)
        result["supabase"] = "online" if r.status_code < 500 else "offline"
    except Exception:
        result["supabase"] = "offline"

    try:
        with _socket.create_connection(("127.0.0.1", 5000), timeout=1.0):
            pass
        result["tcp_server"] = "online"
    except Exception:
        result["tcp_server"] = "offline"

    return result


@app.get("/protegida")
def rota_protegida(usuario: str = Depends(get_current_user)):
    logger.info("Acesso à rota protegida: usuário=%s", usuario)
    return {"mensagem": f"Olá, {usuario}. Sua rota protegida está funcionando."}
