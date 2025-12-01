FROM debian:bookworm-slim

# Install essential utilities (coreutils includes cat, sleep needed by docker-in-docker)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    build-essential \
    coreutils \
    procps \
    openssh-client \
    nano \
    curl \
    git \
    iputils-ping \
    ca-certificates \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create vscode user and grant sudo privileges
RUN useradd -m -s /bin/bash -u 1000 vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to vscode user
USER vscode

# Install uv and add it to PATH (install for vscode user)
ADD --chown=vscode:vscode https://astral.sh/uv/install.sh /tmp/uv-installer.sh
RUN sh /tmp/uv-installer.sh && rm /tmp/uv-installer.sh
ENV PATH="/home/vscode/.local/bin:$PATH"

# Suppress UV hardlink warnings in dev containers
ENV UV_LINK_MODE=copy

WORKDIR /workspace
