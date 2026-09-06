import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rest_framework.test import APIClient
from core.models import Users, Roles, Patients, Notifications

client = APIClient()

def print_result(test_name, success, message):
    status = "PASS" if success else "FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"   -> {message}")

# Helper to get JWT token
def get_token(username, password):
    resp = client.post('/api/auth/token/', {'username': username, 'password': password}, format='json')
    return resp.data['access']

print("\n--- Running Security Verification Tests ---\n")

# --- 2. Privilege Escalation Test ---
resp = client.post('/api/auth/register/', {
    'username': 'sneaky_user',
    'email': 'sneaky@test.com',
    'password': 'password123',
    'role_id': 1 # Trying to become Admin
}, format='json')

sneaky_user = Users.objects.get(username='sneaky_user')
is_patient = sneaky_user.role_id.role_name == 'Patient'
print_result("Privilege Escalation Test", is_patient, 
             f"Tried injecting role_id=1. Actual assigned role: {sneaky_user.role_id.role_name}")

# --- Setup for Isolation Tests ---
client.post('/api/auth/register/', {
    'username': 'patient_b',
    'email': 'patient_b@test.com',
    'password': 'password123'
}, format='json')

token_a = get_token('sneaky_user', 'password123')

client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_a)

# --- 1. Password Leak Test ---
resp = client.get('/api/app/patients/')
data = resp.data
has_password = False
if len(data) > 0:
    first_patient = data[0]
    if 'password' in first_patient:
        has_password = True
    if 'user' in first_patient and 'password' in first_patient['user']:
        has_password = True
        
print_result("Password Leak Test", not has_password, 
             "Checked GET /api/app/patients/ response for 'password' field.")

# --- 3. Data Isolation Test ---
num_patients = len(data)
is_isolated = num_patients == 1 and data[0]['user']['username'] == 'sneaky_user'
print_result("Data Isolation Test", is_isolated, 
             f"Logged in as Patient A. Received {num_patients} patient records. Expected 1.")

# --- 4. AI Analytics Write-Block Test ---
resp = client.post('/api/app/analytics/', {
    'plan_id': 1,
    'predicted_recovery_weeks': 5
}, format='json')

is_blocked = resp.status_code == 403
print_result("AI Analytics Write-Block Test", is_blocked, 
             f"POST /api/app/analytics/ as Patient. Received status code {resp.status_code}. Expected 403.")

print("\n--- Verification Complete ---\n")
