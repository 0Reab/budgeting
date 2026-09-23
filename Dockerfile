# syntax=docker/dockerfile:1
FROM python:3.11.16-slim-trixie@sha256:da047cb8f9d1d98e5c070f5300ba9f7274e33b8fc0e5be5ed88740aed1b95ba9

# enviroment variables
ENV PORT=1337 \
    PIP_NO_CACHE_DIR=1

# install os packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        gfortran \
        pkg-config \
        libopenblas-dev \
        libxcb1 \
        libgl1 \
        libglib2.0-0 \
        libzbar0 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# setup user
RUN useradd -ms /bin/bash budgetapp
USER budgetapp
WORKDIR /home/budgetapp

# install python packages & cpu only torch (ommit line if using gpu)
COPY requirements.txt .
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt

COPY . .

# health check
HEALTHCHECK --interval=1m --timeout=3s --retries=3 \
    CMD curl --fail http://localhost:${PORT}/health || exit 1 # <- sanity check

# run application
EXPOSE ${PORT}
CMD ["python", "-u", "-m", "server.app"]
