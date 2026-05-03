import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student.settings')
django.setup()

from app2.models import Logindata
from django.contrib.auth.hashers import make_password, is_password_usable

accounts = Logindata.objects.all()
count = 0

for acc in accounts:
    # Check if it's already a valid Django hash (Django hashes start with an algorithm name like 'pbkdf2_sha256$')
    if not acc.password.startswith('pbkdf2_'):
        print(f"🔒 Hashing password for: {acc.email}")
        acc.password = make_password(acc.password)
        acc.save()
        count += 1

print(f"\n✅ Successfully encrypted {count} passwords in the database!")
