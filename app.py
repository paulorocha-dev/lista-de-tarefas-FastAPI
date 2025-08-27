from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="API de Tarefas",
    description="Uma API simples para gerenciar tarefas.",
    version="1.0.0",
    contact={
        "name": "Paulo Henrique",
        "email": "paulo.souzarocha27@gmail.com"
    }
)

minhas_tarefas = []

class Tarefa(BaseModel):
    nome_tarefa: str
    descricao_tarefa: str
    tarefa_concluida: bool = False

@app.get("/tarefas")
def get_tarefas():
    if not minhas_tarefas:
        return {"message": "Nenhuma tarefa cadastrada."}
    else:
        return {"tarefas": minhas_tarefas}

@app.post("/adiciona")
def post_tarefas(tarefa: Tarefa):
    for minha_tarefa in minhas_tarefas:
        if minha_tarefa["nome_tarefa"] == tarefa.nome_tarefa:
            raise HTTPException(status_code=400, detail="Tarefa já cadastrada.")
    minhas_tarefas.append(tarefa.model_dump())
    return {"message": "Tarefa adicionada com sucesso."}

@app.put("/atualiza/{nome_tarefa}")
def put_tarefas(nome_tarefa: str, tarefa: Tarefa):
    for minha_tarefa in minhas_tarefas:
        if minha_tarefa["nome_tarefa"] == nome_tarefa:
            minha_tarefa["descricao_tarefa"] = tarefa.descricao_tarefa
            minha_tarefa["tarefa_concluida"] = tarefa.tarefa_concluida
            return {"message": "Tarefa atualizada com sucesso."}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

@app.delete("/deletar/{nome_tarefa}")
def delete_tarefas(nome_tarefa: str):
    for minha_tarefa in minhas_tarefas:
        if minha_tarefa["nome_tarefa"] == nome_tarefa:
            minhas_tarefas.remove(minha_tarefa)
            return {"message": "Tarefa deletada com sucesso."}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
