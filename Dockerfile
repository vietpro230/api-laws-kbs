# ===============================
# 1️⃣ Base builder stage
# ===============================
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for layer caching)
COPY ./generation/requirements.txt .

# Add temporary swap (prevents OOM during pip install)
RUN fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile \
 && pip install --no-cache-dir --upgrade pip wheel setuptools \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt \
 && swapoff /swapfile && rm /swapfile

# ===============================
# 2️⃣ Final runtime stage
# ===============================
FROM python:3.9-slim

WORKDIR /app

# Install minimal runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libopenblas0 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy your app code
COPY ./generation /app/generation
COPY ./data /app/data

# Install CPU-only PyTorch (lighter, no CUDA)
ENV TORCH_CPU_VERSION=2.2.2
RUN pip install --no-cache-dir torch==$TORCH_CPU_VERSION+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Expose FastAPI port
EXPOSE 80

# Start the FastAPI server
CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
