from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import api_views

urlpatterns = [
    # Auth
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/register/', api_views.register_patient, name='api_register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', api_views.get_me, name='api_me'),
    
    # Patient APIs
    path('patient/plan/', api_views.patient_plan, name='api_patient_plan'),
    path('patient/progress/', api_views.patient_progress, name='api_patient_progress'),
    path('patient/appointments/', api_views.patient_appointments, name='api_patient_appointments'),
    
    # Clinician APIs
    path('clinician/patients/', api_views.clinician_patients, name='api_clinician_patients'),
    path('clinician/patients/<int:patient_id>/', api_views.clinician_patient_detail, name='api_clinician_patient_detail'),
    path('clinician/patients/<int:patient_id>/progress/add/', api_views.clinician_progress_add, name='api_clinician_progress_add'),
    path('clinician/availability/', api_views.clinician_availability, name='api_clinician_availability'),
    path('clinician/appointments/', api_views.clinician_appointments, name='api_clinician_appointments'),
    
    # Shared APIs
    path('notifications/', api_views.notifications, name='api_notifications'),
]
