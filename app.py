from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List
import secrets

app = FastAPI(
    title="API de Tarefas",
    description="Uma API simples para gerenciar tarefas.",
    version="1.0.0",
    contact={
        "name": "Paulo Henrique",
        "email": "paulo.souzarocha27@gmail.com"
    }
)

meu_usuario = "admin"
minha_senha = "admin123"

security = HTTPBasic()

minhas_tarefas: List['Tarefa'] = []

class Tarefa(BaseModel):
    nome_tarefa: str
    descricao_tarefa: str
    tarefa_concluida: bool = False

def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, meu_usuario)
    is_password_correct = secrets.compare_digest(credentials.password, minha_senha)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas.",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/tarefas")
def get_tarefas(
    page: int = 1, 
    limit: int = 10,
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros inválidos. 'page' e 'limit' devem ser maiores que 0.")

    if not minhas_tarefas:
        return {"message": "Nenhuma tarefa cadastrada."}
    
    # Ordenação fixa pelo nome da tarefa
    tarefas_ordenadas = sorted(minhas_tarefas, key=lambda x: x.nome_tarefa)

    start = (page - 1) * limit
    end = start + limit

    tarefas_paginadas = [
        {"nome_tarefa": tarefa_data.nome_tarefa, "descricao_tarefa": tarefa_data.descricao_tarefa, "tarefa_concluida": tarefa_data.tarefa_concluida}
        for tarefa_data in tarefas_ordenadas[start:end]
    ]

    return {
        "page": page,
        "limit": limit,
        "total_tarefas": len(minhas_tarefas),
        "tarefas": tarefas_paginadas
    }

@app.post("/adiciona")
def post_tarefas(tarefa: Tarefa, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    for minha_tarefa in minhas_tarefas:
        if minha_tarefa.nome_tarefa == tarefa.nome_tarefa:
            raise HTTPException(status_code=400, detail="Tarefa já cadastrada.")
    minhas_tarefas.append(tarefa)
    return {"message": "Tarefa adicionada com sucesso."}

@app.put("/atualiza/{nome_tarefa}")
def put_tarefas(nome_tarefa: str, tarefa: Tarefa, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    for minha_tarefa in minhas_tarefas:
        if minha_tarefa.nome_tarefa == nome_tarefa:
            minha_tarefa.descricao_tarefa = tarefa.descricao_tarefa
            minha_tarefa.tarefa_concluida = tarefa.tarefa_concluida
            return {"message": "Tarefa atualizada com sucesso."}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

@app.delete("/deletar/{nome_tarefa}")
def delete_tarefas(nome_tarefa: str, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    for minha_tarefa in minhas_tarefas:
        if minha_tarefa.nome_tarefa == nome_tarefa:
            minhas_tarefas.remove(minha_tarefa)
            return {"message": "Tarefa deletada com sucesso."}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
