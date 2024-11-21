FROM python:3.9-slim

WORKDIR /app

# Copier uniquement les fichiers nécessaires
COPY order_app/ /app/

# Installer les dépendances si `requirements.txt` existe dans `order_app`
RUN pip install --no-cache-dir -r /app/requirements.txt || echo "No requirements.txt found"

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
