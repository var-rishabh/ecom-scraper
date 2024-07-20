FROM python:3.10.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

EXPOSE 8000

CMD uvicorn main:app --reload --port 8000 --host 0.0.0.0