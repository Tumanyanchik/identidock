FROM jenkins/jenkins:2.563

USER root

# Устанавливаем зависимости для добавления репозитория Docker
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    sudo \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Добавляем официальный GPG-ключ Docker (новый метод)
RUN mkdir -p /usr/share/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | \
       gpg --dearmor -o /usr/share/keyrings/docker.gpg

# Добавляем официальный репозиторий Docker
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] \
    https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list

# Устанавливаем Docker CE (клиент + демон, если нужен демон внутри контейнера)
RUN apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io \
    && rm -rf /var/lib/apt/lists/*

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

USER jenkins
