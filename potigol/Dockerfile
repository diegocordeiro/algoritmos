#FROM gitpod/workspace-full (comentado para deixar de usar a imagem maior do Gitpod)
FROM alpine:3.19

USER root

# Instala Python + dependências
RUN apk add --no-cache python3 py3-pip openjdk17-jre-headless curl bash

# Baixa o jar do Potigol
RUN curl -L -o /usr/local/lib/potigol.jar https://github.com/potigol/potigol/releases/download/0.9.15/potigol.jar

# Cria o script potigol no PATH
RUN printf '#!/bin/bash\njava -jar /usr/local/lib/potigol.jar "$@"\n' > /usr/local/bin/potigol \
    && chmod +x /usr/local/bin/potigol

# Cria ambiente virtual para Python
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Instala FastAPI e Uvicorn dentro do ambiente virtual
RUN pip install --no-cache-dir fastapi uvicorn python-multipart "uvicorn[standard]"

# Define pasta de trabalho
WORKDIR /app

# Copia a API
COPY api.py /app/api.py

# Expõe a porta
EXPOSE 8001

# Mantém o processo rodando
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
