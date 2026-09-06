from django.urls import path
from . import views_portal

urlpatterns = [
    path('login/', views_portal.portal_login, name='portal_login'),
    path('register/', views_portal.portal_register, name='portal_register'),
    path('logout/', views_portal.portal_logout, name='portal_logout'),
    
    # Phase 2 Stub
    path('dashboard/', views_portal.portal_dashboard, name='portal_dashboard'),
    
    # Phase 3
    path('plan/', views_portal.patient_rehab_plan, name='portal_rehab_plan'),
    
    # Phase 4 (Clinician)
    path('patients/', views_portal.clinician_patients_list, name='portal_patients_list'),
    path('patients/<int:patient_id>/', views_portal.clinician_patient_detail, name='portal_patient_detail'),
    path('availability/', views_portal.clinician_availability, name='portal_availability'),
    
    # Phase 5 (Shared)
    path('appointments/', views_portal.portal_appointments, name='portal_appointments'),
    path('notifications/', views_portal.portal_notifications, name='portal_notifications'),
    
    # Phase 6 (Reporting)
    path('reports/<int:plan_id>/download/', views_portal.generate_clinical_report, name='download_report'),
]
