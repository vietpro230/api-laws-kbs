FROM python:3.9-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# copy only requirements first to leverage cache (file is in generation/)
COPY ./generation/requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --prefer-binary --no-cache-dir -r /app/requirements.txt \
 && rm -rf /root/.cache/pip

# copy application code and data
COPY ./generation /app/generation
COPY ./data /app/data

EXPOSE 80

CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
