
FROM python:3.9


WORKDIR /


COPY ./requirements.txt /generation/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /generation/requirements.txt

COPY ./generation /generation
COPY ./data /data


CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
