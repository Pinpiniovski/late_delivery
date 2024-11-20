# Utiliser une image de base légère de Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . /app

# Exposer le port sur lequel l'application va tourner
EXPOSE 5001

# Démarrer l'application
CMD ["python", "app.py"]
