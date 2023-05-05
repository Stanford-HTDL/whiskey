FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./_api_keys.json /app/_api_keys.json

COPY ./whiskey/api /app/api

# COPY ./whiskey/celery_config /app/celery_config


