from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import datetime

def get_fernet():
    # Use the Django SECRET_KEY to derive a 32-byte url-safe base64 key
    key_bytes = settings.SECRET_KEY.encode('utf-8')
    # Pad or truncate to exactly 32 bytes
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b'0')
    else:
        key_bytes = key_bytes[:32]
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)

class EncryptedCharField(models.CharField):
    description = "A CharField that automatically encrypts data at rest."

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        fernet = get_fernet()
        # Encrypt the string
        encrypted = fernet.encrypt(str(value).encode('utf-8'))
        return encrypted.decode('utf-8')

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            fernet = get_fernet()
            decrypted = fernet.decrypt(value.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception:
            # If decryption fails, return the raw value
            return value


class EncryptedDateField(models.DateField):
    description = "A DateField that automatically encrypts data at rest."

    def get_internal_type(self):
        # Tell Django to use a CharField in the database so we can store the long encrypted string
        return "CharField"

    def db_type(self, connection):
        return 'varchar(255)'

    def get_prep_value(self, value):
        if not value:
            return value
        fernet = get_fernet()
        # Convert date to string before encrypting
        str_val = str(value)
        encrypted = fernet.encrypt(str_val.encode('utf-8'))
        return encrypted.decode('utf-8')

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            fernet = get_fernet()
            decrypted_str = fernet.decrypt(value.encode('utf-8')).decode('utf-8')
            # Parse the YYYY-MM-DD string back into a date object
            if '-' in decrypted_str:
                parts = decrypted_str.split('-')
                if len(parts) == 3:
                    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            return decrypted_str
        except Exception:
            return value
