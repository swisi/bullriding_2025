from app import db

def init_db():
    # Stellen Sie sicher, dass der Pfad zur Datenbankdatei korrekt ist
    db.create_all()

if __name__ == "__main__":
    init_db()
