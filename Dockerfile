FROM python:3.9-slim

WORKDIR /app

COPY order_app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY order_app/ /app

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
