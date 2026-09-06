import os
import django
from django.utils import timezone
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Users, Clinicians, Clinician_Availability

def seed_availability():
    clinicians = Clinicians.objects.all()
    today = timezone.now().date()
    
    for clinician in clinicians:
        # Clear existing future slots to avoid duplicates during test
        Clinician_Availability.objects.filter(clinician_id=clinician, date__gte=today).delete()
        
        for i in range(14):
            date = today + datetime.timedelta(days=i)
            # Skip Sundays
            if date.weekday() == 6:
                continue
                
            Clinician_Availability.objects.create(
                clinician_id=clinician,
                date=date,
                start_time=datetime.time(9, 0), # 9 AM
                end_time=datetime.time(17, 0),  # 5 PM
                is_leave=False,
                reason=""
            )
        print(f"Generated 14 days schedule for Clinician ID: {clinician.id}")

if __name__ == '__main__':
    seed_availability()
