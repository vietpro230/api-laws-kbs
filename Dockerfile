FROM python:3.11-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# copy only requirements first to leverage cache
COPY ./generation/requirements.txt /tmp/requirements.txt

# remove any 'torch' lines and install other deps first, then install torch from PyTorch CPU wheel
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates wget build-essential \
 && python -m pip install --upgrade pip setuptools wheel \
 && sed -E '/^torch/Id' /tmp/requirements.txt > /tmp/reqs_no_torch.txt \
 && pip install --prefer-binary --no-cache-dir -r /tmp/reqs_no_torch.txt \
 && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
 && apt-get remove -y build-essential \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/* /tmp/*

# copy project and data
COPY ./generation /app/generation
COPY ./data /app/data

EXPOSE 80

CMD ["uvicorn", "generation.main:app", "--host", "0.0.0.0", "--port", "80"]
