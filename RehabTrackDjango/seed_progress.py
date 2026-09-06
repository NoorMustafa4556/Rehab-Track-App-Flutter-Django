import os
import django
from django.utils import timezone
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Rehabilitation_Plans, Assessment_Metrics, Progress_Logs, Progress_Metric_Values, Users

def seed_progress_for_all():
    plans = Rehabilitation_Plans.objects.filter(status='Active')
    if not plans.exists():
        print("No active rehab plans found.")
        return

    pain_metric, _ = Assessment_Metrics.objects.get_or_create(
        metric_name="Pain Level", 
        unit="1-10", 
        defaults={'min_value': 1, 'max_value': 10}
    )
    rom_metric, _ = Assessment_Metrics.objects.get_or_create(
        metric_name="Range of Motion", 
        unit="Degrees", 
        defaults={'min_value': 0, 'max_value': 180}
    )
    
    creator = Users.objects.filter(role_id__role_name='Clinician').first() or Users.objects.first()

    Progress_Logs.objects.all().delete()
    print("Cleared all old logs...")

    base_date = timezone.now().date() - datetime.timedelta(days=14)
    
    trends = [
        {"pain": 8, "rom": 45, "notes": "Initial stiffness and high pain."},
        {"pain": 7, "rom": 55, "notes": "Slight improvement after heat therapy."},
        {"pain": 5, "rom": 75, "notes": "Pain reducing, able to stretch further."},
        {"pain": 4, "rom": 90, "notes": "Significant mobility gained."},
        {"pain": 2, "rom": 110, "notes": "Excellent progress. Patient reports feeling great."}
    ]

    for plan in plans:
        print(f"Seeding for Plan ID: {plan.id} (Patient: {plan.patient_id.user_id.username})")
        for i, data in enumerate(trends):
            log_date = base_date + datetime.timedelta(days=i*3)
            
            log = Progress_Logs.objects.create(
                plan_id=plan,
                log_date=log_date,
                treatment_given=f"Session {i+1}: Standard physical therapy routine.",
                clinician_notes=data["notes"],
                created_by=creator
            )
            
            Progress_Metric_Values.objects.create(
                log_id=log,
                metric_id=pain_metric,
                value=data["pain"]
            )
            
            Progress_Metric_Values.objects.create(
                log_id=log,
                metric_id=rom_metric,
                value=data["rom"]
            )

    print("Successfully seeded dynamic progress data for all active plans!")

if __name__ == '__main__':
    seed_progress_for_all()
