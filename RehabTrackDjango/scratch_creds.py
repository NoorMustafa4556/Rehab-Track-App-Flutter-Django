import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Users, Roles

def reset_clinician_password():
    clinicians = Users.objects.filter(role_id__role_name='Clinician')
    
    if not clinicians.exists():
        print("No Clinician accounts found in the database. Creating one...")
        role = Roles.objects.get(role_name='Clinician')
        clinician = Users.objects.create_user(
            username='dr_smith',
            email='dr_smith@example.com',
            password='password123',
            role_id=role
        )
        print(f"Created new Clinician: Username: {clinician.username}, Password: password123")
    else:
        print("Found the following Clinicians:")
        for clinician in clinicians:
            clinician.set_password('password123')
            clinician.save()
            print(f"- Username: {clinician.username} | Password: password123")

if __name__ == '__main__':
    reset_clinician_password()
