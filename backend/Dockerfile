FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 --retries 5 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
COPY app/ ./app/
COPY alembic.ini ./
COPY alembic/ ./alembic/
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","1"]
