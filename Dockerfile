FROM python:3.11

WORKDIR /app/generation

COPY ./generation/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./generation /app/generation
COPY ./data /app/data

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
