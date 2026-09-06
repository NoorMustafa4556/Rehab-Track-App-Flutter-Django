from django.urls import path
from . import views_admin

urlpatterns = [
    path('login/', views_admin.admin_login, name='admin_login'),
    path('logout/', views_admin.admin_logout, name='admin_logout'),
    path('dashboard/', views_admin.dashboard, name='admin_dashboard'),
    path('activity-logs/', views_admin.activity_logs, name='admin_activity_logs'),
    path('reports/', views_admin.reports_viewer, name='admin_reports'),
    
    path('users/', views_admin.users_management, name='admin_users'),
    path('clinicians/', views_admin.clinicians_management, name='admin_clinicians'),
    path('clinicians/<int:clinician_id>/', views_admin.clinician_detail, name='admin_clinician_detail'),
    path('patients/', views_admin.patients_management, name='admin_patients'),
    path('patients/<int:patient_id>/', views_admin.patient_detail, name='admin_patient_detail'),
    path('patients/<int:patient_id>/delete/', views_admin.delete_patient, name='admin_delete_patient'),
    
    path('appointments/', views_admin.appointments_management, name='admin_appointments'),
    path('resources/', views_admin.resources_management, name='admin_resources'),
    path('resources/<int:resource_id>/delete/', views_admin.delete_resource, name='admin_delete_resource'),
    
    path('settings/lookups/', views_admin.system_lookups, name='admin_lookups'),
    path('settings/lookups/<str:lookup_type>/<int:lookup_id>/delete/', views_admin.delete_lookup, name='admin_delete_lookup'),
    
    path('role-permissions/', views_admin.role_permissions_view, name='admin_role_permissions'),
]
