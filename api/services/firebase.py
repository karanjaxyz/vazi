import firebase_admin
from firebase_admin import auth, credentials

_app: firebase_admin.App | None = None


def init_firebase(credentials_path: str | None = None) -> None:
    """Initialize Firebase Admin SDK. Call once on startup.

    If credentials_path is None, uses GOOGLE_APPLICATION_CREDENTIALS env var
    or Application Default Credentials (works in Cloud Run, etc.).
    """
    global _app
    if _app is not None:
        return

    cred = (
        credentials.Certificate(credentials_path)
        if credentials_path
        else credentials.ApplicationDefault()
    )
    _app = firebase_admin.initialize_app(cred)


def verify_token(id_token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims.

    Returns dict with at least:
        - uid: str
        - email: str (if available)

    Raises firebase_admin.auth.InvalidIdTokenError if invalid.
    Raises firebase_admin.auth.ExpiredIdTokenError if expired.
    """
    decoded = auth.verify_id_token(id_token)
    return {
        "uid": decoded["uid"],
        "email": decoded.get("email"),
    }
