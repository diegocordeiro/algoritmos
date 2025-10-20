#FROM gitpod/workspace-full (comentado para deixar de usar a imagem maior do Gitpod)
FROM alpine:3.19

USER root

# Instala Python + dependências
#RUN apt-get update && apt-get install -y python3 python3-pip curl openjdk-17-jre-headless (comentado para deixar de usar a imagem maior do Gitpod)
RUN apk add --no-cache python3 py3-pip openjdk21-jre-headless curl bash
# Baixa o jar do Potigol
RUN curl -L -o /usr/local/lib/potigol.jar https://github.com/potigol/potigol/releases/download/1.0.0-RC2/potigol.jar

# Cria o script potigol no PATH
#RUN echo '#!/bin/bash\n\njava -jar /usr/local/lib/potigol.jar "$@"' > /usr/local/bin/potigol \
#    && chmod +x /usr/local/bin/potigol (comentado para deixar de usar a imagem maior do Gitpod)
RUN apk add --no-cache bash \
    && printf '#!/bin/bash\njava -jar /usr/local/lib/potigol.jar "$@"\n' > /usr/local/bin/potigol \
    && chmod +x /usr/local/bin/potigol

# Instala FastAPI e Uvicorn
#RUN pip3 install --no-cache-dir fastapi uvicorn python-multipart "uvicorn[standard]" (comentado para deixar de usar a imagem maior do Gitpod)
RUN pip install --no-cache-dir fastapi uvicorn python-multipart "uvicorn[standard]"
# Define pasta de trabalho
WORKDIR /app

# Copia a API
COPY api.py /app/api.py

# Expõe a porta
EXPOSE 8001

# Mantém o processo rodando
CMD ["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
