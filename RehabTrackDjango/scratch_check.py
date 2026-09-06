import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Progress_Logs, Progress_Metric_Values, Rehabilitation_Plans, Patients

print("--- PLANS ---")
for p in Rehabilitation_Plans.objects.all():
    print(f"Plan ID: {p.id}, Patient: {p.patient_id.user_id.username}, Status: {p.status}")

print("\n--- LOGS ---")
for l in Progress_Logs.objects.all():
    print(f"Log ID: {l.id}, Plan ID: {l.plan_id.id}, Date: {l.log_date}")

print("\n--- METRICS ---")
for pmv in Progress_Metric_Values.objects.all():
    print(f"PMV ID: {pmv.id}, Log ID: {pmv.log_id.id}, Metric: {pmv.metric_id.metric_name}, Value: {pmv.value}")
