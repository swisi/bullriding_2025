import os
import re


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
    # Helper: parse byte sizes like "16MB", "10 MiB", or raw bytes
    def _parse_size_bytes(value, default): # type: ignore
        if value is None:
            return default
        # If already numeric
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value)
        s = str(value).strip().lower()
        if not s:
            return default
        # Plain integer string
        if s.isdigit():
            return int(s)
        # Match formats like 16mb, 16 mib, 1.5g, 500k, 20 bytes
        m = re.match(r"^(\d+(?:\.\d+)?)\s*([kmgt]?i?b?|bytes?)$", s)
        if not m:
            # Try without trailing 'b' if user wrote just '16m'
            m = re.match(r"^(\d+(?:\.\d+)?)\s*([kmgt])$", s)
        if not m:
            return default
        num = float(m.group(1))
        unit = m.group(2)
        unit = unit.lower()
        units = {
            "b": 1,
            "byte": 1,
            "bytes": 1,
            "k": 1024,
            "kb": 1024,
            "kib": 1024,
            "m": 1024 ** 2,
            "mb": 1024 ** 2,
            "mib": 1024 ** 2,
            "g": 1024 ** 3,
            "gb": 1024 ** 3,
            "gib": 1024 ** 3,
            "t": 1024 ** 4,
            "tb": 1024 ** 4,
            "tib": 1024 ** 4,
        }
        multiplier = units.get(unit, None)
        if multiplier is None:
            return default
        return int(num * multiplier)

    MAX_CONTENT_LENGTH = _parse_size_bytes(
        os.getenv("MAX_CONTENT_LENGTH"), 16 * 1024 * 1024 # type: ignore
    )  # 16MB default
    # Feature flags
    ALLOW_REGISTRATION = os.getenv("ALLOW_REGISTRATION", "false").lower() in ("1", "true", "yes")
