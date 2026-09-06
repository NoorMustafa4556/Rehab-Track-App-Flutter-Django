from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    PatientRegistrationView, RoleViewSet, SpecializationViewSet, ResourceTypeViewSet,
    AssessmentMetricViewSet, ResourceViewSet, UserViewSet, PatientViewSet,
    ClinicianViewSet, ClinicianAvailabilityViewSet, RehabilitationPlanViewSet,
    ProgressLogViewSet, AppointmentViewSet, NotificationViewSet, AIAnalyticsViewSet,
    ClinicalReportViewSet, ActivityLogViewSet
)

# App Router (Flutter Facing)
app_router = DefaultRouter()
app_router.register(r'patients', PatientViewSet, basename='patient')
app_router.register(r'clinicians', ClinicianViewSet, basename='clinician')
app_router.register(r'availability', ClinicianAvailabilityViewSet, basename='clinician-availability')
app_router.register(r'plans', RehabilitationPlanViewSet, basename='rehab-plan')
app_router.register(r'progress-logs', ProgressLogViewSet, basename='progress-log')
app_router.register(r'appointments', AppointmentViewSet, basename='appointment')
app_router.register(r'notifications', NotificationViewSet, basename='notification')
app_router.register(r'analytics', AIAnalyticsViewSet, basename='ai-analytics')
app_router.register(r'reports', ClinicalReportViewSet, basename='clinical-report')

# Admin Router
admin_router = DefaultRouter()
admin_router.register(r'roles', RoleViewSet, basename='role')
admin_router.register(r'specializations', SpecializationViewSet, basename='specialization')
admin_router.register(r'resource-types', ResourceTypeViewSet, basename='resource-type')
admin_router.register(r'assessment-metrics', AssessmentMetricViewSet, basename='assessment-metric')
admin_router.register(r'resources', ResourceViewSet, basename='resource')
admin_router.register(r'users', UserViewSet, basename='user')
admin_router.register(r'activity-logs', ActivityLogViewSet, basename='activity-log')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', PatientRegistrationView.as_view(), name='auth_register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App endpoints
    path('app/', include(app_router.urls)),
    
    # Admin endpoints
    path('admin/', include(admin_router.urls)),
]
