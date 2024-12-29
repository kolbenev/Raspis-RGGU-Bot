FROM python:3.13

WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY database database/
COPY config config/
COPY parser parser/
COPY bot bot/

ENV PYTHONPATH=/app
ENV TZ=Europe/Moscow

CMD ["bash", "-c", "cd database && alembic upgrade head && python ../bot/main.py"]