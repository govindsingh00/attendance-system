"""
encryption.py
Smart Attendance Management System
Role: Cybersecurity - Data Encryption Module
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode
import os

# ─── Key Generation ───────────────────────────────────────────────────────────

def generate_key() -> bytes:
    """Generate and save a Fernet encryption key."""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as f:
        f.write(key)
    return key

def load_key() -> bytes:
    """Load the saved encryption key."""
    with open("secret.key", "rb") as f:
        return f.read()

def derive_key_from_password(password: str, salt: bytes = None):
    """Derive a secure key from a password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key), salt

# ─── Encrypt / Decrypt ────────────────────────────────────────────────────────

def encrypt_data(data: str, key: bytes) -> bytes:
    """Encrypt attendance data."""
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(token: bytes, key: bytes) -> str:
    """Decrypt attendance data."""
    f = Fernet(key)
    return f.decrypt(token).decode()
