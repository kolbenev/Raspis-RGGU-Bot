FROM python:3.12

WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY database/confdb.py database/
COPY database/getter_variables.py database/
COPY database/models.py database/

COPY config config/
COPY parser parser/
COPY bot bot/

ENV PYTHONPATH=/app

CMD ["python", "bot/main.py"]