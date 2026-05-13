\# Projeto Home - Fase 8



API backend construída com FastAPI, autenticação JWT, rota protegida, integração com banco local e testes automatizados com pytest.



\## Stack

\- FastAPI

\- PostgreSQL / Supabase local

\- JWT

\- Pytest

\- GitHub Actions



\## Como iniciar o projeto



\### 1. Subir o Supabase local

```bash

npx supabase start

```



\### 2. Subir o backend

```bash

uvicorn app.main:app --reload

```



\### 3. Rodar os testes

```bash

python -m pytest tests/test\_auth.py

```



\## Rotas principais

\- `/health`

\- `/auth/token`

\- `/protegida`



\## Status da fase

Fase 8 concluída com autenticação, rota protegida e testes automatizados.

