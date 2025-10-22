from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
import secrets
import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(
    title="API de Tarefas",
    description="Uma API simples para gerenciar tarefas.",
    version="1.0.0",
    contact={
        "name": "Paulo Henrique",
        "email": "paulo.souzarocha27@gmail.com"
    }
)

MEU_USUARIO = os.getenv("MEU_USUARIO")
MINHA_SENHA = os.getenv("MINHA_SENHA")

security = HTTPBasic()

class TarefaDB(Base):
    __tablename__ = "Tarefas"

    id = Column(Integer, primary_key=True, index=True)
    nome_tarefa = Column(String, unique=True, index=True)
    descricao_tarefa = Column(String)
    tarefa_concluida = Column(Boolean, default=False, index=True)

class Tarefa(BaseModel):
    nome_tarefa: str
    descricao_tarefa: str
    tarefa_concluida: bool = False

Base.metadata.create_all(bind=engine)

def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, MINHA_SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )
    
@app.get("/")

def hello_world():
    return {"message": "Olá, Mundo! A API de Tarefas está funcionando."}

@app.get("/tarefas")
def get_tarefas(
    page: int = 1,
    limit: int = 10,
    ordenar_por: Optional[str] = Query("nome_tarefa", regex="^(id|nome_tarefa|descricao_tarefa|tarefa_concluida)$"),
    direcao: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros inválidos. 'page' e 'limit' devem ser maiores que 0.")

    order_func = asc if direcao == "asc" else desc
    tarefas = db.query(TarefaDB)\
                .order_by(order_func(getattr(TarefaDB, ordenar_por)))\
                .offset((page - 1) * limit)\
                .limit(limit)\
                .all()

    total_tarefas = db.query(TarefaDB).count()

    return {
        "page": page,
        "limit": limit,
        "total_tarefas": total_tarefas,
        "tarefas": [{
            "id": tarefa.id,
            "nome_tarefa": tarefa.nome_tarefa,
            "descricao_tarefa": tarefa.descricao_tarefa,
            "tarefa_concluida": tarefa.tarefa_concluida
        } for tarefa in tarefas]
    }

@app.post("/adiciona")
def post_tarefas(tarefa: Tarefa, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_tarefa = db.query(TarefaDB).filter(TarefaDB.nome_tarefa == tarefa.nome_tarefa).first()
    if db_tarefa:
        raise HTTPException(status_code=400, detail="Tarefa com esse nome já existe.")
    
    nova_tarefa = TarefaDB(
        nome_tarefa=tarefa.nome_tarefa,
        descricao_tarefa=tarefa.descricao_tarefa,
        tarefa_concluida=tarefa.tarefa_concluida
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)

    return {"message": "Tarefa adicionada com sucesso."}
    
@app.put("/atualiza/{nome_tarefa}")
def put_tarefas(nome_tarefa: str, tarefa: Tarefa, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_tarefa = db.query(TarefaDB).filter(TarefaDB.nome_tarefa == nome_tarefa).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    db_tarefa.nome_tarefa = tarefa.nome_tarefa
    db_tarefa.descricao_tarefa = tarefa.descricao_tarefa
    db_tarefa.tarefa_concluida = tarefa.tarefa_concluida

    db.commit()
    db.refresh(db_tarefa)

    return {"message": "Tarefa atualizada com sucesso."}

@app.delete("/deletar/{nome_tarefa}")
def delete_tarefas(nome_tarefa: str, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    db_tarefa = db.query(TarefaDB).filter(TarefaDB.nome_tarefa == nome_tarefa).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    db.delete(db_tarefa)
    db.commit()

    return {"message": "Tarefa deletada com sucesso."}
