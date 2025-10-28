# ===============================
# 1️⃣ Base builder stage
# ===============================
FROM python:3.9-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for layer caching)
COPY ./requirements.txt .

# Add temporary swap (to prevent OOM during pip install)
RUN fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile \
 && pip install --no-cache-dir --upgrade pip wheel setuptools \
 && pip install --no-cache-dir --prefer-binary -r requirements.txt \
 && swapoff /swapfile && rm /swapfile

# ===============================
# 2️⃣ Final runtime stage
# ===============================
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install only minimal runtime libs (for PyMuPDF, numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libopenblas-base \
 && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY ./generation /app/generation
COPY ./data /app/data

# Use CPU-only PyTorch (lighter, faster to install)
ENV TORCH_CPU_VERSION=2.2.2
RUN pip install --no-cache-dir torch==$TORCH_CPU_VERSION+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Expose the FastAPI port
EXPOSE 80

# Start FastAPI app via Uvicorn
CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
