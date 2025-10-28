# ===============================
# 2️⃣ Final runtime stage
# ===============================
FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libopenblas0 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source
COPY ./generation /app/generation
COPY ./data /app/data

# Install CPU-only PyTorch
ENV TORCH_CPU_VERSION=2.2.2
RUN pip install --no-cache-dir torch==$TORCH_CPU_VERSION+cpu -f https://download.pytorch.org/whl/torch_stable.html

EXPOSE 80
CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
