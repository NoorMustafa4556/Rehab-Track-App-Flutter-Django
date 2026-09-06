import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Users

def reset_sneaky_user():
    try:
        user = Users.objects.get(username='sneaky_user')
        user.set_password('password123')
        user.save()
        print(f"Username: {user.username} | Password: password123")
    except Users.DoesNotExist:
        print("User 'sneaky_user' not found!")

if __name__ == '__main__':
    reset_sneaky_user()
