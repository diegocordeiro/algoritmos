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

# Fila global de jobs
job_queue = asyncio.Queue()
MAX_CONCURRENT = 2  # limite de processos simultâneos
active_processes = {}

class Job:
    def __init__(self, file: UploadFile):
        self.file = file
        self.session_id = None
        self.proc = None
        self.tmp_path = None
        self.ready_event = asyncio.Event()  # sinaliza quando processo iniciou

@app.on_event("startup")
async def startup_event():
    async def worker():
        while True:
            job = await job_queue.get()
            try:
                while len(active_processes) >= MAX_CONCURRENT:
                    await asyncio.sleep(0.5)

                # Cria arquivo temporário
                fd, tmp_path = tempfile.mkstemp(suffix=".poti")
                with os.fdopen(fd, "wb") as tmp:
                    tmp.write(await job.file.read())

                # Inicia processo
                proc = subprocess.Popen(
                    ["timeout", "30s", "potigol", tmp_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                job.session_id = proc.pid
                job.proc = proc
                job.tmp_path = tmp_path

                active_processes[job.session_id] = job
                job.ready_event.set()  # libera quem estava esperando
            except Exception as e:
                print(f"Erro ao processar job: {e}")
            finally:
                job_queue.task_done()

    asyncio.create_task(worker())

@app.post("/start/")
async def start_potigol(file: UploadFile = File(...)):
    job = Job(file)
    await job_queue.put(job)

    # Posição na fila
    queue_list = list(job_queue._queue)
    position = queue_list.index(job) + 1  # posição 1 = primeiro da fila

    # Se já estiver pronto, a posição será 0
    await job.ready_event.wait()
    started = True

    return {
        "session_id": job.session_id,
        "queue_position": 0 if started else position
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    if session_id not in active_processes:
        await websocket.send_text("⚠️ Sessão inválida ou ainda na fila")
        await websocket.close()
        return

    job = active_processes[session_id]
    proc = job.proc

    async def read_output(stream, prefix=""):
        loop = asyncio.get_running_loop()
        while True:
            line = await loop.run_in_executor(None, stream.readline)
            if line == "":
                break
            await websocket.send_text(prefix + line)

    asyncio.create_task(read_output(proc.stdout))
    asyncio.create_task(read_output(proc.stderr, prefix="[ERR] "))

    try:
        while True:
            if proc.poll() is not None:
                if proc.returncode == 124:
                    await websocket.send_text("⚠️ Loop infinito ou execução excedeu tempo de execução máximo.")
                else:
                    await websocket.send_text("✅ Processo finalizado")
                break

            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1)
                if data.strip().lower() == "exit":
                    proc.terminate()
                    await websocket.send_text("🔴 Encerrado pelo usuário")
                    break
                else:
                    if proc.stdin:
                        proc.stdin.write(data + "\n")
                        proc.stdin.flush()
            except asyncio.TimeoutError:
                continue
    finally:
        if proc.poll() is None:
            proc.terminate()
        if os.path.exists(job.tmp_path):
            os.remove(job.tmp_path)
        del active_processes[session_id]
        await websocket.close()