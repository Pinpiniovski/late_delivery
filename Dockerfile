# Base Python image
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY order_app/ /app
COPY scripts/ /scripts
COPY requirements.txt /app

# Installer les dépendances
RUN pip install -r /app/requirements.txt

# Commande par défaut pour démarrer Flask
CMD ["sh", "-c", "python /scripts/preprocess_orders.py && python /app/app.py"]
