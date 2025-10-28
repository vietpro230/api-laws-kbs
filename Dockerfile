FROM python:3.11-slim

# Sử dụng slim để tránh musl/alpine issues với nhiều wheel
FROM python:3.9-slim

WORKDIR /code

# giảm bộ nhớ dùng bởi pip và tắt kiểm tra phiên bản pip
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# copy requirements trước để tận dụng cache layer
COPY ./generation/requirements.txt /generation/requirements.txt

# nâng cấp pip & cài requirements (prefer binary để tránh build from source)
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && python -m pip install --upgrade pip setuptools wheel \
 && pip install --prefer-binary --no-cache-dir -r /generation/requirements.txt \
 && apt-get remove -y ca-certificates \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# copy toàn bộ thư mục generation và data
COPY ./generation /generation
COPY ./data /data

EXPOSE 80

CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
