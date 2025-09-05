
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

RUN sh -c '(echo "#!/usr/bin/env sh" && curl -L https://github.com/potigol/potigol/releases/download/1.0.0-RC1/potigol.jar) > /usr/local/lib/potigol.jar'

RUN echo '#!/bin/bash\n\njava -jar /usr/local/lib/potigol.jar "$@" 2> /dev/null' > /usr/local/bin/potigol \
    && chmod +x /usr/local/bin/potigol
```

---

## docker-compose.yml

```yaml
version: "3.8"

services:
  potigol:
    build: .
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
   docker compose run --rm potigol hello.poti
   ```

---

## Opção 2 – Abrir no VS Code (Dev Containers)

1. Instale no VS Code a extensão **Dev Containers**.
2. Crie a pasta `.devcontainer/` com o arquivo abaixo:

**.devcontainer/devcontainer.json**

```json
{
  "name": "Potigol",
  "dockerComposeFile": "docker-compose.yml",
  "service": "potigol",
  "workspaceFolder": "/workspace",
  "settings": {
    "terminal.integrated.defaultProfile.linux": "bash"
  },
  "extensions": [
    "ms-azuretools.vscode-docker"
  ]
}
```

3. No VS Code:

   * Abra a paleta de comandos (`Ctrl+Shift+P` / `Cmd+Shift+P` no Mac).
   * Selecione **Dev Containers: Reopen in Container**.
   * O VS Code vai montar o ambiente dentro do container.

4. Rode o programa no terminal integrado:

   ```sh
   potigol hello.poti
   ```

---

## ⚡ Opção 3 – VS Code Tasks (atalho Ctrl+Shift+B)

Se quiser rodar **direto do editor**, sem abrir terminal:

1. Crie a pasta `.vscode/` na raiz do projeto.
2. Adicione o arquivo abaixo:

**.vscode/tasks.json**

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Rodar Potigol",
      "type": "shell",
      "command": "docker compose run --rm potigol ${fileBasename}",
      "options": {
        "cwd": "${fileDirname}"
      },
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "problemMatcher": []
    }
  ]
}
```

3. Abra um arquivo `.poti` no VS Code.
4. Pressione **Ctrl+Shift+B** (ou **Cmd+Shift+B** no Mac).
5. O programa será executado no container automaticamente.
