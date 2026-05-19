Smart Attendance Management System
Role: Cybersecurity - Authentication & Session Security
"""

import hashlib
import hmac
import os
import jwt
import datetime

SECRET_KEY = os.environ.get("JWT_SECRET", "change-this-in-production")

# ─── Password Hashing ─────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash."""
    salt_hex, key_hex = stored_hash.split(":")
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return hmac.compare_digest(key.hex(), key_hex)

# ─── JWT Tokens ───────────────────────────────────────────────────────────────

def generate_token(user_id: str, role: str) -> str:
    """Generate a signed JWT token."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")
