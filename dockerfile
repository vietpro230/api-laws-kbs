
FROM python:3.9


WORKDIR /app


COPY ./requirements.txt /generation/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /generation/requirements.txt

COPY ./generation app/generation
COPY ./data app/data


CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
