from fastapi import FastAPI, HTTPException

app = FastAPI()

minhas_tarefas = {}

@app.get("/tarefas")
def get_tarefas():
    if not minhas_tarefas:
        return {"message": "Nenhuma tarefa cadastrada."}
    else:
        return {"tarefas": minhas_tarefas}

@app.post("/adiciona")
def post_tarefas(id_tarefa: int, nome_tarefa: str, descricao_tarefa: str, tarefa_concluida: bool = False):
    if id_tarefa in minhas_tarefas:
        raise HTTPException(status_code=400, detail="Tarefa já cadastrada.")
    else:
        minhas_tarefas[id_tarefa] = {
            "nome_tarefa": nome_tarefa,
            "descricao_tarefa": descricao_tarefa,
            "tarefa_concluida": tarefa_concluida
        }
        return {"message": "Tarefa adicionada com sucesso."}

@app.put("/atualiza/{id_tarefa}")
def put_tarefas(id_tarefa: int, nome_tarefa: str = None, descricao_tarefa: str = None, tarefa_concluida: bool = None):
    minha_tarefa = minhas_tarefas.get(id_tarefa)
    if not minha_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    else:
        if nome_tarefa is not None:
            minha_tarefa["nome_tarefa"] = nome_tarefa
        if descricao_tarefa is not None:
            minha_tarefa["descricao_tarefa"] = descricao_tarefa
        if tarefa_concluida is not None:
            minha_tarefa["tarefa_concluida"] = tarefa_concluida
        return {"message": "Tarefa atualizada com sucesso."}

@app.delete("/deletar/{id_tarefa}")
def delete_tarefas(id_tarefa: int):
    if id_tarefa in minhas_tarefas:
        del minhas_tarefas[id_tarefa]
        return {"message": "Tarefa deletada com sucesso."}
    else:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
