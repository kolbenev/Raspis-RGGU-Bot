FROM python:3.12

WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY database database/

COPY config config/
COPY parser parser/
COPY bot bot/

ENV PYTHONPATH=/app

CMD ["bash", "-c", "cd database && alembic upgrade head && python ../bot/main.py"]