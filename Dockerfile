# ===============================
# 1️⃣ Base builder stage
# ===============================
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY ./generation/requirements.txt .

# Add temporary swap to prevent OOM during pip install
RUN fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile \
 && pip install --no-cache-dir --upgrade pip wheel setuptools \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt \
 && swapoff /swapfile && rm /swapfile

# ===============================
# 2️⃣ Final runtime stage
# ===============================
FROM python:3.9-slim

WORKDIR /app

# Install minimal runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libopenblas-base \
 && rm -rf /var/lib/apt/lists/*

# Copy Python environment from builder
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source
COPY ./generation /app/generation
COPY ./data /app/data

# Use CPU-only Torch (lighter)
ENV TORCH_CPU_VERSION=2.2.2
RUN pip install --no-cache-dir torch==$TORCH_CPU_VERSION+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Expose API port
EXPOSE 80

# Launch FastAPI app
CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
