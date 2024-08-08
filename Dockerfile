FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR app/
COPY . .

RUN apt-get update -y

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

RUN chmod 777 ./entrypoint.sh

EXPOSE 8000
CMD poetry run fastapi run madr_book/app.py --host 0.0.0.0