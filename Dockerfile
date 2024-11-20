FROM python:3.9-slim

WORKDIR /app

COPY order_app/ /app/

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--timeout", "120", "app:app"]
