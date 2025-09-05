
# 🐳 Ambiente Potigol com Docker e VS Code

Este guia mostra como configurar e executar programas **Potigol** usando **Docker** e integrando ao **VS Code**.
Você pode optar por rodar os arquivos direto pelo `docker compose`, abrir o projeto dentro de um **Dev Container**, ou ainda rodar via **tasks do VS Code**.

---

## Estrutura de arquivos

```
.
├── Dockerfile
├── docker-compose.yml
├── .devcontainer/ (opcional, para VS Code)
│   └── devcontainer.json
├── .vscode/ (opcional, para tasks no VS Code)
│   └── tasks.json
└── codigo/
    └── hello.poti
```

---

## Dockerfile

```dockerfile
FROM gitpod/workspace-full

USER root

# Baixa o jar e coloca em /usr/local/lib
RUN curl -L -o /usr/local/lib/potigol.jar https://github.com/potigol/potigol/releases/download/1.0.0-RC1/potigol.jar

# Cria o script potigol no PATH
RUN echo '#!/bin/bash\n\njava -jar /usr/local/lib/potigol.jar "$@" 2> /dev/null' > /usr/local/bin/potigol \
    && chmod +x /usr/local/bin/potigol

# Volta para usuário padrão
USER gitpod

```

---

## docker-compose.yml

```yaml
version: "3.8"

services:
  potigol:
    build: .
    platform: linux/amd64
    container_name: potigol
    tty: true
    stdin_open: true
    volumes:
      - ./codigo:/workspace
    working_dir: /workspace
    entrypoint: ["potigol"]

```

---

## Opção 1 – Executar direto pelo Docker Compose

1. Crie a pasta `codigo/` e coloque seu arquivo Potigol, por exemplo `hello.poti`.
2. Construa a imagem:

   ```sh
   docker compose build
   ```
3. Execute seu programa diretamente:

   ```sh
   docker compose run --rm --entrypoint /bin/bash potigol
   ```

   ```sh
   Dentro do container:
   potigol seu-arquivo.poti
   ```
