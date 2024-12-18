FROM python:3.10.5-alpine

WORKDIR /app

RUN apk update && \
    apk add --no-cache \
    musl-dev \
    libc-dev \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
