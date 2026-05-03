import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student.settings')
django.setup()

from app2.models import Logindata
from django.contrib.auth.hashers import make_password

student_email = "student@gmail.com"
new_password = "studentpassword"

try:
    acc = Logindata.objects.get(email=student_email, usertype="student")
    acc.password = make_password(new_password)
    acc.save()
    print(f"\n✅ Student password forcefully reset!")
    print(f"📧 Email: {student_email}")
    print(f"🔑 New Password: {new_password}")
    print("\nYou can now log in at http://127.0.0.1:8000/login/")
except Logindata.DoesNotExist:
    print(f"\n⚠️ Could not find a student account with email: {student_email}")
    print("Please login as Admin to create a new student.")
