import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student.settings')
django.setup()

from app2.models import Admindata, Logindata

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
        password=password,
        usertype="admin"
    )
    print(f"\n✅ Initial Admin created successfully!")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print("\nYou can now go to http://127.0.0.1:8000/login/ and sign in to access the system.")
else:
    print("\n⚠️ Admin account already exists. Please use admin@smartattend.com / adminpassword")
