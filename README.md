# Mechanical Bullriding 2025

Flask-App zur Verwaltung eines Bullriding-Wettbewerbs: Teilnehmer erfassen/bearbeiten, Zeiten pflegen, Rundenlogik (Vorrunden, Zwischenrunde, Finale) und Rangliste. Produktion per Docker/Gunicorn oder vorgefertigtem Container-Image (GHCR).

## Inhalt
- Features & Screens
- Architektur
- Quick Start (lokal, Docker, GHCR)
- Konfiguration (.env)
- Admin & Benutzer
- GitHub Actions (manueller Image‑Build)
- Datenbank & Migrationen
- Wettbewerbsmodus

## Features & Screens
- Teilnehmerverwaltung (Erfassen, Bearbeiten, Löschen) mit Foto‑Upload.
- Zeitenerfassung VR/ZR/Finale, automatische Topzeiten.
- Abschluss-Buttons je Runde mit Qualifikationslogik.
- Rangliste sortiert nach Top Final → Top ZR → Top VR.
- Authentifizierung (Login/Logout). Registrierung optional per Flag.
- Admin-Aktionen: Resultate/Teilnehmer zurücksetzen.
- Live: Teilnehmerdetails, drei Blöcke (VR, ZR, Final) nebeneinander.
- Stage: wie Live, ohne Navbar, fest im Dark‑Mode; pollingbasiert ohne „Flackern“ (Reload nur bei Wechsel des aktiven Teilnehmers).

## Architektur
- Flask App‑Factory: `app/__init__.py`, Blueprint: `app/routes.py`.
- ORM/DB: SQLAlchemy + Flask‑SQLAlchemy, Migrationen via Flask‑Migrate.
- Auth: Flask‑Login, Forms/CSRF: Flask‑WTF.
- Templates: Jinja2 + Bootstrap 4.
- Navbar ausgelagert: `app/templates/_navbar.html` (via `{% include %}`).

## Quick Start

### Lokal (Entwicklung)
Voraussetzungen: Python 3.12

1. Virtualenv & Dependencies
   - Linux/macOS: `python -m venv venv && source venv/bin/activate`
   - Windows: `python -m venv venv && .\\venv\\Scripts\\Activate.ps1`
   - `pip install -r requirements.txt`
2. `.env` anpassen (siehe unten) und DB migrieren: `flask db upgrade`
3. Start: `flask run --host=0.0.0.0 --port 5000`

### Docker Compose (mit GHCR Image)
Beispiel `docker-compose.yml` (bereit im Repo):

```yaml
services:
  web:
    image: ghcr.io/<owner>/<repo>:latest
    ports:
      - "5025:5000"
    environment:
      - SECRET_KEY=change-me
      - DATABASE_URL=sqlite:////app/database/site.db
    volumes:
      - db-data:/app/database
    restart: always
volumes:
  db-data:
```

Start: `docker compose pull && docker compose up -d`

### Eigenes Image lokal bauen
```bash
docker build -t bullriding:local .
docker run --rm -p 5000:5000 bullriding:local
```

## Konfiguration (.env)
- `SECRET_KEY`: erforderlich in Produktion (CSRF/Session).
- `DATABASE_URL`: z. B. `sqlite:////app/database/site.db` (Default ist SQLite unter `database/site.db`).
- `SITE_NAME`: Anzeigename in der Navbar und im Titel.
- `ALLOW_REGISTRATION`: `true/false` (Standard: false). Steuert, ob „Register“ im Menü auftaucht und `/register` erlaubt ist.
- `MAX_CONTENT_LENGTH`: Uploadlimit in Bytes (Default 16MB).
- `FLASK_ENV`: `production` (Default im Container) oder `development`.

Alle Flags werden über `.env` lokal oder via Docker‑Env gesetzt.

## Admin & Benutzer
- Passwort ändern: Eingeloggt unter `/password` (über Admin‑Menü verlinkt).
- Registrierung: Route `/register` ist nur aktiv, wenn `ALLOW_REGISTRATION=true`. Andernfalls redirect nach Login; im Menü wird der „Register“-Eintrag ausgeblendet.
- Erste Nutzeranlage (falls Registrierung deaktiviert): per Flask‑Shell z. B.

```py
flask shell
>>> from app import db
>>> from app.models import User
>>> u = User(username='admin', email='you@example.com')
>>> u.set_password('GEHEIM'); db.session.add(u); db.session.commit()
```

## GitHub Actions (manueller Build zu GHCR)
- Workflow: `.github/workflows/docker.yml` (Name: `docker-image-manual`).
- Start manuell in GitHub → Actions → Run workflow.
- Inputs:
  - `tag`: gewünschter Imagetag (z. B. `v1.0.0`, `manual`).
  - `platforms`: Default `linux/amd64,linux/arm64`.
  - `latest`: optional zusätzlich `:latest` pushen.
- Ergebnis: `ghcr.io/<owner>/<repo>:<tag>` (und optional `:latest`).

## Datenbank & Migrationen
- Migration ausführen: `flask db upgrade` (lokal oder im Container mit `docker compose exec web flask db upgrade`).
- Migration erstellen: `flask db migrate -m "..."` und anschließend `flask db upgrade`.

## Wettbewerbsmodus
Kurzüberblick der Logik in `app/routes.py` → `finish_round`:
- Vorrunden (VR1–VR3): automatische Qualifikation ab 99s; Top‑5 werden aufgefüllt.
- Zwischenrunde (ZR): beste der zwei Zeiten zählt; Top‑10 in Finale.
- Finale: beste Finalzeit als `toptime_Finalrunde`.

## Live & Stage
- Live: normale Seite mit Navbar/Theme, drei Ergebnisblöcke (VR/ZR/Final) nebeneinander.
- Stage: gleiche Darstellung ohne Navbar, Dark‑Mode fest. Polling alle 5s über `/active_id`; Reload nur bei Wechsel des aktiven Teilnehmers (vermeidet Flackern).

