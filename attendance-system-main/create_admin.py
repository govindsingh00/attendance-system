import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student.settings')
django.setup()

from app2.models import Admindata, Logindata
from django.contrib.auth.hashers import make_password

# Create Admin data
email = "admin@smartattend.com"
password = "adminpassword"

if not Logindata.objects.filter(email=email).exists():
    Admindata.objects.create(
        name="Super Admin",
        email=email,
        contact="9999999999",
        address="College Campus"
    )
    Logindata.objects.create(
        email=email,
        password=make_password(password),
        usertype="admin"
    )
    print(f"\n✅ Initial Admin created successfully!")
else:
    # Force update the password in case it was lost or improperly hashed
    acc = Logindata.objects.get(email=email)
    acc.password = make_password(password)
    acc.save()
    print(f"\n✅ Admin account already existed. Password has been forcefully reset!")

print(f"📧 Email: {email}")
print(f"🔑 Password: {password}")
print("\nYou can now go to http://127.0.0.1:8000/login/ and sign in to access the system.")
