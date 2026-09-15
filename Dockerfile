# syntax=docker/dockerfile:1
FROM python:3.11.16-slim-trixie

# install os packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    pkg-config \
    libopenblas-dev \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    libzbar0

COPY . .

# install python packages & cpu only torch (ommit pip torch line if using gpu)
RUN pip install torch torchvision --no-cache-dir --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# run application
EXPOSE 1337
CMD ["python","-u","-m","server.app"]
