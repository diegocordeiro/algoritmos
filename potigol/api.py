import subprocess
import tempfile
import os
import asyncio 
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir requisições do Django
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://professordiegocordeiro.com.br"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guardar os processos em memória (id -> processo)
processos = {}
# Processo único (sem WebSocket)
# Desativado para evitar problemas com múltiplos usuários
# @app.post("/run/")
# async def run_potigol(file: UploadFile = File(...)):
#     tmp_path = None
#     try:
#         fd, tmp_path = tempfile.mkstemp(suffix=".poti")
#         with os.fdopen(fd, "wb") as tmp:
#             tmp.write(await file.read())

#         # Usa timeout do Linux para matar loops infinitos
#         result = subprocess.run(
#             ["timeout", "30s", "potigol", tmp_path],
#             capture_output=True,
#             text=True,
#             input=""  # força EOF
#         )

#         if result.returncode == 124:  # código do timeout
#             return JSONResponse({
#                 "error": "Processo encerrado automaticamente: possível loop infinito ou código mal executado. Revise seu código."
#             }, status_code=408)

#         return JSONResponse({
#             "stdout": result.stdout,
#             "stderr": result.stderr,
#             "exit_code": result.returncode
#         })

#     except Exception as e:
#         import traceback
#         return JSONResponse({"error": traceback.format_exc()}, status_code=500)

#     finally:
#         if tmp_path and os.path.exists(tmp_path):
#             os.remove(tmp_path)


@app.post("/start/")
async def start_potigol(file: UploadFile = File(...)):
    fd, tmp_path = tempfile.mkstemp(suffix=".poti")
    with os.fdopen(fd, "wb") as tmp:
        tmp.write(await file.read())

    # Executa o processo com timeout do Linux
    proc = subprocess.Popen(
        ["timeout", "120s", "potigol", tmp_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    pid = proc.pid
    processos[pid] = {
        "process": proc,
        "file": tmp_path
    }

    return {"session_id": pid}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()

    if session_id not in processos:
        await websocket.send_text("Sessão inválida ou expirada")
        await websocket.close()
        return

    proc = processos[session_id]["process"]

    async def read_output(stream, prefix=""):
        loop = asyncio.get_running_loop()
        while True:
            line = await loop.run_in_executor(None, stream.readline)
            if line == "":
                break
            await websocket.send_text(prefix + line)

    # inicia leitura de stdout e stderr
    asyncio.create_task(read_output(proc.stdout))
    asyncio.create_task(read_output(proc.stderr, prefix="[ERR] "))

    try:
        while True:
            # se processo terminou, encerra a sessão
            if proc.poll() is not None:
                if proc.returncode == 124:
                    await websocket.send_text("⚠️ Processo encerrado automaticamente: possível loop infinito ou código mal executado. Revise seu código.")
                else:
                    await websocket.send_text("Processo finalizado")
                break

            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1)
                if data.strip().lower() == "exit":
                    proc.terminate()
                    await websocket.send_text("Processo encerrado pelo usuário")
                    break
                else:
                    if proc.stdin:
                        proc.stdin.write(data + "\n")
                        proc.stdin.flush()
            except asyncio.TimeoutError:
                continue  # apenas verifica novamente se o processo terminou

    except Exception as e:
        await websocket.send_text(f"[ERRO] {e}")
    finally:
        # garante que o processo seja encerrado mesmo em loop infinito
        if proc.poll() is None:
            proc.terminate()
        tmp_path = processos[session_id]["file"]
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        del processos[session_id]
        await websocket.close()
