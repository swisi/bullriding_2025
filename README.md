# bullriding_2024

Flask-Anwendung zur Verwaltung eines mechanischen Bullriding-Wettbewerbs: Teilnehmer erfassen/bearbeiten, Zeiten pflegen, Rundenlogik (Vorrunden, Zwischenrunde, Finale) anwenden und Rangliste anzeigen. Produktions-Setup über Docker + gunicorn.

## Inhalt
- Überblick & Features
- Architektur & Tech-Stack
- Setup (lokal & Docker)
- Konfiguration (ENV Variablen)
- Datenbank & Migrationen
- Nützliche Befehle
- Wettbewerbsmodus

## Überblick & Features
- Teilnehmerverwaltung (Erfassen, Bearbeiten, Löschen)
- Zeitenerfassung für Runden, inklusive Topzeiten (VR/ZR/Finale)
- Abschluss der Runden mit Qualifikationslogik
- Rangliste (sortiert nach Final-, Zwischen- und Vorrunden-Topzeiten)
- Authentifizierung (Login/Logout, Registrierung)
- Admin-Operationen (Resultate/Teilnehmer zurücksetzen)

## Architektur & Tech-Stack
- Backend: Flask 3, Blueprint (`app/routes.py`), App-Factory (`app/__init__.py`)
- ORM/DB: SQLAlchemy 2, Flask‑SQLAlchemy, Alembic (Flask‑Migrate)
- Auth: Flask‑Login
- Forms/CSRF: Flask‑WTF
- Templates: Jinja2 + Bootstrap 4
- Produktion: gunicorn (per Docker)

## Setup (lokal)
Voraussetzungen: Python 3.12, virtualenv empfohlen.

1) Abhängigkeiten installieren
   - `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
   - `pip install -r requirements.txt`

2) ENV setzen (mindestens SECRET_KEY)
   - Linux/macOS: `export FLASK_APP=wsgi:app FLASK_ENV=development SECRET_KEY=dev-secret`
   - Windows (PowerShell): `$env:FLASK_APP='wsgi:app'; $env:FLASK_ENV='development'; $env:SECRET_KEY='dev-secret'`

3) Datenbank migrieren
   - `flask db upgrade`

4) Starten (nur für Entwicklung)
   - `flask run --host=0.0.0.0 --port 5000`

## Setup (Docker)
Build & Run via Compose:

```bash
docker compose up --build
```

Die App läuft auf `http://localhost:5000`.

## Konfiguration (ENV Variablen)
- `SECRET_KEY` (erforderlich in Produktion): kryptographischer Schlüssel (CSRF/Session)
- `DATABASE_URL` (optional): z. B. `sqlite:////app/database/site.db` (Default)
- `FLASK_APP`: für CLI, gesetzt auf `wsgi:app`
- `FLASK_ENV`: `production` (Default in Docker) oder `development`

In `docker-compose.yml` sind sinnvolle Defaults hinterlegt. Ändere `SECRET_KEY` unbedingt.

## Datenbank & Migrationen
- Alembic/Flask‑Migrate verwalten Schemaänderungen.
- Bei Start im Container wird automatisch `flask db upgrade` ausgeführt (siehe `entrypoint.sh`).
- Lokal: `flask db migrate -m "Nachricht"` (Schemaänderung generieren) und `flask db upgrade` ausführen.

## Nützliche Befehle
- Datenbank migrieren: `flask db upgrade`
- Migration generieren: `flask db migrate -m "..."`
- Dev‑Server: `flask run --host=0.0.0.0 --port 5000`
- Tests (optional, falls hinzugefügt): `pytest`

## Wettbewerbsmodus

### Runden 1–3 (Vorrunden)
- Teilnehmer mit 99 Sekunden in einer Vorrunde qualifizieren automatisch weiter.
- Die besten 5 jeder Vorrunde qualifizieren (Auffüllen bis 5 falls nötig).

### Runden 4–5 (Zwischenrunde)
- Jeder Teilnehmer hat zwei Läufe, die beste Zeit zählt (`toptime_Zwischenrunde`).
- Die besten 10 qualifizieren für die Finalrunde.

### Runde 6 (Finalrunde)
- Bester Ritt zählt (`toptime_Finalrunde`).
