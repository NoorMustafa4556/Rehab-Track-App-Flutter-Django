import os
import sys
import django

# Setup Django
sys.path.insert(0, r'c:\Users\NoorMustafa4556\Desktop\Sir Jawad Project\RehabTrackDjango')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from core.models import Resource_Types, Activity_Logs, Patients, Clinicians, Resources

def main():
    print("--- SEEDING RESOURCE TYPES ---")
    types = ["Room", "Equipment", "Machine", "Device"]
    for t in types:
        rt, created = Resource_Types.objects.get_or_create(name=t)
        if created:
            print(f"Created Resource_Type: {t}")
        else:
            print(f"Resource_Type {t} already exists.")
            
    print("\n--- SIMULATING UI ACTIONS FOR ACTIVITY LOGS ---")
    c = Client()
    # Login as admin
    login_success = c.post('/admin-panel/login/', {'username': 'admin', 'password': 'Admin123!'})
    print(f"Admin login status: {login_success.status_code} (Expect 302)")

    # 1. Create a Rehab Plan
    patient = Patients.objects.first()
    clinician = Clinicians.objects.first()
    if patient and clinician:
        res1 = c.post(f'/admin-panel/patients/{patient.id}/', {
            'clinician_id': clinician.id,
            'start_date': '2026-08-17',
            'goals': 'Improve mobility'
        })
        print(f"Create Rehab Plan status: {res1.status_code}")

    # 2. Add a Resource
    res_type = Resource_Types.objects.first()
    if res_type:
        res2 = c.post('/admin-panel/resources/', {
            'name': 'Test Treadmill 5000',
            'type_id': res_type.id
        })
        print(f"Add Resource status: {res2.status_code}")

    # 3. Soft-delete the Resource
    new_res = Resources.objects.filter(name='Test Treadmill 5000').last()
    if new_res:
        res3 = c.post(f'/admin-panel/resources/{new_res.id}/delete/')
        print(f"Delete Resource status: {res3.status_code}")
        
    print("\n--- VERIFYING ACTIVITY LOGS IN DB ---")
    logs = Activity_Logs.objects.all().order_by('-timestamp')[:5]
    print(f"Total Activity_Logs count: {Activity_Logs.objects.count()}")
    for log in logs:
        print(f"- [{log.action}] {log.description} (IP: {log.ip_address})")

if __name__ == '__main__':
    main()
