from rest_framework import viewsets, permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    Roles, Users, Specializations, Resource_Types, Patients,
    Clinicians, Clinician_Availability, Resources, Rehabilitation_Plans,
    Assessment_Metrics, Progress_Logs, Progress_Metric_Values,
    Appointments, AI_Analytics, Clinical_Reports, Notifications, Activity_Logs
)
from .serializers import (
    RoleSerializer, UserSerializer, PatientRegistrationSerializer,
    SpecializationSerializer, ResourceTypeSerializer, PatientSerializer,
    ClinicianSerializer, ClinicianAvailabilitySerializer, ResourceSerializer,
    RehabilitationPlanSerializer, AssessmentMetricSerializer, ProgressLogSerializer,
    ProgressMetricValueSerializer, AppointmentSerializer, AIAnalyticsSerializer,
    ClinicalReportSerializer, NotificationSerializer, ActivityLogSerializer
)
from .permissions import IsAdmin, IsClinician, IsPatient, IsAdminOrReadOnly

class PatientRegistrationView(CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = PatientRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminOrReadOnly]

class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specializations.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAdminOrReadOnly]

class ResourceTypeViewSet(viewsets.ModelViewSet):
    queryset = Resource_Types.objects.all()
    serializer_class = ResourceTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

class AssessmentMetricViewSet(viewsets.ModelViewSet):
    queryset = Assessment_Metrics.objects.all()
    serializer_class = AssessmentMetricSerializer
    permission_classes = [IsAdminOrReadOnly]

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminOrReadOnly]

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Patients.objects.all()
        elif user.role_id and user.role_id.role_name == 'Patient':
            return Patients.objects.filter(user_id=user)
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            if clinician:
                plan_patient_ids = Rehabilitation_Plans.objects.filter(clinician_id=clinician).values_list('patient_id', flat=True)
                return Patients.objects.filter(id__in=plan_patient_ids)
            return Patients.objects.none()
        return Patients.objects.none()

class ClinicianViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicianSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Clinicians.objects.all()
        if self.request.method in permissions.SAFE_METHODS:
            return Clinicians.objects.all()
        elif user.role_id and user.role_id.role_name == 'Clinician':
            return Clinicians.objects.filter(user_id=user)
        return Clinicians.objects.none()

class ClinicianAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicianAvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Clinician_Availability.objects.all()
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            if clinician:
                return Clinician_Availability.objects.filter(clinician_id=clinician)
            return Clinician_Availability.objects.none()
        if self.request.method in permissions.SAFE_METHODS:
            return Clinician_Availability.objects.all()
        return Clinician_Availability.objects.none()

class RehabilitationPlanViewSet(viewsets.ModelViewSet):
    serializer_class = RehabilitationPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Rehabilitation_Plans.objects.all()
        elif user.role_id and user.role_id.role_name == 'Patient':
            patient = getattr(user, 'patient_profile', None)
            return Rehabilitation_Plans.objects.filter(patient_id=patient) if patient else Rehabilitation_Plans.objects.none()
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            return Rehabilitation_Plans.objects.filter(clinician_id=clinician) if clinician else Rehabilitation_Plans.objects.none()
        return Rehabilitation_Plans.objects.none()

class ProgressLogViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Progress_Logs.objects.all()
        elif user.role_id and user.role_id.role_name == 'Patient':
            patient = getattr(user, 'patient_profile', None)
            if patient:
                plans = Rehabilitation_Plans.objects.filter(patient_id=patient)
                return Progress_Logs.objects.filter(plan_id__in=plans)
            return Progress_Logs.objects.none()
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            if clinician:
                plans = Rehabilitation_Plans.objects.filter(clinician_id=clinician)
                return Progress_Logs.objects.filter(plan_id__in=plans)
            return Progress_Logs.objects.none()
        return Progress_Logs.objects.none()

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Appointments.objects.all()
        elif user.role_id and user.role_id.role_name == 'Patient':
            patient = getattr(user, 'patient_profile', None)
            return Appointments.objects.filter(patient_id=patient) if patient else Appointments.objects.none()
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            return Appointments.objects.filter(clinician_id=clinician) if clinician else Appointments.objects.none()
        return Appointments.objects.none()

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Notifications.objects.all()
        return Notifications.objects.filter(user_id=user)

class AIAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = AIAnalyticsSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()] 

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return AI_Analytics.objects.all()
        elif user.role_id and user.role_id.role_name == 'Patient':
            patient = getattr(user, 'patient_profile', None)
            if patient:
                plans = Rehabilitation_Plans.objects.filter(patient_id=patient)
                return AI_Analytics.objects.filter(plan_id__in=plans)
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            if clinician:
                plans = Rehabilitation_Plans.objects.filter(clinician_id=clinician)
                return AI_Analytics.objects.filter(plan_id__in=plans)
        return AI_Analytics.objects.none()

class ClinicalReportViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicalReportSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsAdmin()] 

    def get_queryset(self):
        user = self.request.user
        if user.role_id and user.role_id.role_name == 'Admin':
            return Clinical_Reports.objects.all()
        elif user.role_id and user.role_id.role_name == 'Patient':
            patient = getattr(user, 'patient_profile', None)
            if patient:
                plans = Rehabilitation_Plans.objects.filter(patient_id=patient)
                return Clinical_Reports.objects.filter(plan_id__in=plans)
        elif user.role_id and user.role_id.role_name == 'Clinician':
            clinician = getattr(user, 'clinician_profile', None)
            if clinician:
                plans = Rehabilitation_Plans.objects.filter(clinician_id=clinician)
                return Clinical_Reports.objects.filter(plan_id__in=plans)
        return Clinical_Reports.objects.none()

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity_Logs.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdmin] 
