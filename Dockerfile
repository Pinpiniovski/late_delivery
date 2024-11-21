FROM python:3.9-slim

WORKDIR /app

# Copier le dossier principal
COPY order_app/ /app/

# Installer les dépendances depuis le nouvel emplacement
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
