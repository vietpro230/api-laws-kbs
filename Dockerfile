# ===============================
# 1️⃣ Giai đoạn build dependencies
# ===============================
FROM python:3.9-slim AS builder

# Thư mục làm việc trong container
WORKDIR /app

# Cài các gói hệ thống cần thiết để build wheel
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements (để tận dụng cache)
COPY ./generation/requirements.txt .

# Cập nhật pip & cài dependencies
RUN pip install --no-cache-dir --upgrade pip wheel setuptools
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# ===============================
# 2️⃣ Giai đoạn runtime (chạy thật)
# ===============================
FROM python:3.9-slim

WORKDIR /app

# Cài các thư viện cần thiết để chạy (không build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libopenblas0 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Sao chép các gói Python đã cài từ builder
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

# Sao chép mã nguồn
COPY ./generation /app/generation
COPY ./data /app/data

# Cài torch CPU-only (nhẹ hơn nhiều)
ENV TORCH_CPU_VERSION=2.2.2
RUN pip install --no-cache-dir torch==$TORCH_CPU_VERSION+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Mở port 80 cho FastAPI
EXPOSE 80

# Lệnh chạy ứng dụng
CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
