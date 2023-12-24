from fastapi_login import LoginManager

from core.config import app_settings

manager = LoginManager(
    secret=app_settings.secret,
    token_url=app_settings.token_url,
    default_expiry=app_settings.token_expires,
)


def hash_password(plaintext_password: str):
    """
    Return the hash of a password.
    """
    return manager.pwd_context.hash(plaintext_password)


def verify_password(password_input: str, hashed_password: str):
    """
    Check if the provided password matches.
    """
    return manager.pwd_context.verify(password_input, hashed_password)
