FROM python:3.10.11-slim

WORKDIR /app

COPY . .

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

EXPOSE 8000

CMD uvicorn main:app --reload --port 8000 --host 0.0.0.0