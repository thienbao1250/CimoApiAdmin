FROM python:3.10-slim

WORKDIR /app

# Cài thêm các thư viện hệ thống cần thiết
RUN apt update && apt install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
