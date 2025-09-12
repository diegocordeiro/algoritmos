FROM gitpod/workspace-full

USER root

# Baixa o jar e coloca em /usr/local/lib
RUN curl -L -o /usr/local/lib/potigol.jar https://github.com/potigol/potigol/releases/download/1.0.0-RC1/potigol.jar

# Cria o script potigol no PATH
RUN echo '#!/bin/bash\n\njava -jar /usr/local/lib/potigol.jar "$@" 2> /dev/null' > /usr/local/bin/potigol \
    && chmod +x /usr/local/bin/potigol

# Volta para usuário padrão
USER gitpod
