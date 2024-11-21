FROM python:3.12.3-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential

RUN pip install --upgrade pip
RUN pip install pipenv --upgrade


WORKDIR /gateway/

COPY Pipfile ./
COPY Pipfile.lock ./

RUN pipenv install --deploy --system

COPY . .

EXPOSE 8000
