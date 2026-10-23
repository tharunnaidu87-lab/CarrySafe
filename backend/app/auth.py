import hashlib
import secrets
from datetime import timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select
from .db import Session, now, utc
from .models import User, LoginSession

hasher = PasswordHasher()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def login(email, password):
    with Session.begin() as db:
        user = db.scalar(select(User).where(User.email == email.lower()))
        if not user:
            # Similar expensive work for unknown accounts.
            hasher.hash(password)
            return None
        try:
            hasher.verify(user.password_hash, password)
        except VerificationError:
            return None
        token = secrets.token_urlsafe(32)
        db.add(LoginSession(token_hash=digest(token), user_id=user.id, expires_at=now() + timedelta(hours=8)))
        return token


def authenticate(token):
    if not token or len(token) > 512:
        return None
    with Session() as db:
        session = db.get(LoginSession, digest(token))
        if not session or utc(session.expires_at) <= now():
            return None
        return db.get(User, session.user_id)
