# Verwenden Sie ein offizielles Python-Image als Basis
FROM python:3.12-slim

# Setzen Sie das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopieren Sie die Anforderungen und installieren Sie sie
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie den Rest des Anwendungscodes
COPY . .

# Erstellen Sie das Verzeichnis für die Datenbank, falls es nicht existiert
RUN mkdir -p /app/database

# Setzen Sie die Flask-Umgebungsvariablen
ENV FLASK_APP=wsgi:app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Exponieren Sie den Port, auf dem die App läuft
EXPOSE 5000

# Kopiere entrypoint.sh und setze Ausführungsrechte
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Festlegen des Entrypoints
ENTRYPOINT ["/app/entrypoint.sh"]

# Starten Sie die Flask-Anwendung
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-t", "120", "-b", "0.0.0.0:5000", "wsgi:app"]
