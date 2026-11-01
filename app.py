"""Entry point. `flask --app app run` for development, `gunicorn app:app` on Render."""
from studyroom import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
