import subprocess
import tempfile
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir requisições do Django
origins = [
    "http://localhost:8000",  # URL do seu frontend Django
    "http://127.0.0.1:8000",
    "https://professordiegocordeiro.com.br"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # ou ["*"] para liberar todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run/")
async def run_potigol(file: UploadFile = File(...)):
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".poti")
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(await file.read())

        result = subprocess.run(
            ["potigol", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
            input=""   # força EOF
        )

        return JSONResponse({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        })

    except subprocess.TimeoutExpired:
        return JSONResponse({
            "error": "Tempo limite excedido (o código não terminou em 30 segundos)"
        }, status_code=408)

    except Exception as e:
        import traceback
        return JSONResponse({"error": traceback.format_exc()}, status_code=500)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
