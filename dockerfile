
FROM python:3.9


WORKDIR /app


COPY ./generation/requirements.txt /app/generation/requirements.txt



RUN pip install --no-cache-dir --upgrade -r /app/generation/requirements.txt

COPY ./generation app/generation
COPY ./data app/data


CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
