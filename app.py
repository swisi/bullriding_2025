from app import create_app

# Minimal WSGI entry; main app factory lives in app/__init__.py
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
