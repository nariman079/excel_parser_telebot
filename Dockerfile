FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /bot/
COPY /poetry.lock pyproject.toml /bot/
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root
COPY ./documents /bot/documents
COPY ./migrations /bot/migrations
COPY ./src /bot/src
COPY ./main_v3.py /bot/main_v3.py
COPY ./.env /bot/