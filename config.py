import os


def _normalize_sqlite_uri(uri: str) -> str:
    # Ensure forward slashes in sqlite file path to be URL-compatible, esp. on Windows
    prefix = "sqlite:///"
    if uri.startswith(prefix):
        path = uri[len(prefix):].replace("\\", "/")
        return prefix + path
    return uri


def _sqlite_uri_absolute(uri: str, base_dir: str) -> str:
    """If sqlite URI has a relative path, make it absolute under base_dir."""
    prefix = "sqlite:///"
    if uri.startswith(prefix):
        path = uri[len(prefix):]
        # Normalize slashes for os.path checks
        norm_path = path.replace("/", os.sep)
        if not os.path.isabs(norm_path):
            abs_path = os.path.abspath(os.path.join(base_dir, norm_path))
            return prefix + abs_path.replace("\\", "/")
    return uri


class Config:
    # Use SECRET_KEY from environment. In development, allow a weak default; in production require env.
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY") or (
        "dev-insecure-secret-key" if FLASK_ENV == "development" else None
    )

    basedir = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(basedir, "database", "site.db")
    default_sqlite_uri = "sqlite:///" + database_path.replace("\\", "/")
    _raw_uri = os.getenv("DATABASE_URL", default_sqlite_uri)
    _raw_uri = _normalize_sqlite_uri(_raw_uri)
    SQLALCHEMY_DATABASE_URI = _sqlite_uri_absolute(_raw_uri, basedir)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # UI configuration
    SITE_NAME = os.getenv("SITE_NAME", "Mechanical Bullriding")
    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB default
    # Feature flags
    ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", "false").lower() in ("1", "true", "yes")
