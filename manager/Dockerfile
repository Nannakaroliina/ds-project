FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

LABEL maintainer="Nanna"

USER root
RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc && \
    apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
COPY manager.py manager.py
COPY game_logic game_logic

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "manager.py" ]