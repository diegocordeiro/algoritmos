FROM gitpod/workspace-full

USER root

# Instala Python + dependências
RUN apt-get update && apt-get install -y python3 python3-pip curl openjdk-17-jre-headless

# Baixa o jar do Potigol
RUN curl -L -o /usr/local/lib/potigol.jar https://github.com/potigol/potigol/releases/download/1.0.0-RC1/potigol.jar

# Cria o script potigol no PATH
RUN echo '#!/bin/bash\n\njava -jar /usr/local/lib/potigol.jar "$@"' > /usr/local/bin/potigol \
    && chmod +x /usr/local/bin/potigol

# Instala FastAPI e Uvicorn
RUN pip3 install --no-cache-dir fastapi uvicorn python-multipart

# Define pasta de trabalho
WORKDIR /app

# Copia a API
COPY api.py /app/api.py

# Expõe a porta
EXPOSE 8001

# Mantém o processo rodando
CMD ["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
