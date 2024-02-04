# please excute the mess that is this dockerfile. i spend 
# forever getting this dependency hell to work.

ARG PYTHON_VERSION=3.10.*
FROM continuumio/miniconda3 as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001

RUN apt-get update --allow-releaseinfo-change && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    pkg-config \
    libhdf5-dev \
    cmake \
    libgl1-mesa-glx

COPY conda-requirements.txt .
RUN conda create -n myenv python=3.10
RUN conda clean --all --yes


RUN conda run -n myenv pip install --upgrade pip
RUN conda run -n myenv pip install --upgrade keras-cv tensorflow
RUN conda run -n myenv pip install --upgrade keras
RUN conda run -n myenv pip install 'uvicorn[standard]'

RUN conda run -n myenv pip install click
RUN conda run -n myenv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN conda run -n myenv python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'

COPY pip-requirements.txt .
RUN conda run -n myenv pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["conda", "run", "-n", "myenv", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]