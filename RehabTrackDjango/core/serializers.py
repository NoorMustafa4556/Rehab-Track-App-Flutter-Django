from rest_framework import serializers
from .models import (
    Users, Roles, Patients, Clinicians, Specializations,
    Clinician_Availability, Rehabilitation_Plans, Assessment_Metrics,
    Progress_Logs, Progress_Metric_Values, Appointments, Notifications
)

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ['id', 'role_name']

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(source='role_id', read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'phone', 'role']

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specializations
        fields = ['id', 'name']

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user_id', read_only=True)
    
    class Meta:
        model = Patients
        fields = ['id', 'user', 'dob', 'gender', 'medical_history', 'created_at']

class ClinicianProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='user_id', read_only=True)
    specialization = SpecializationSerializer(source='specialization_id', read_only=True)
    
    class Meta:
        model = Clinicians
        fields = ['id', 'user', 'specialization', 'is_available']

class RehabilitationPlanSerializer(serializers.ModelSerializer):
    clinician = ClinicianProfileSerializer(source='clinician_id', read_only=True)
    patient = PatientProfileSerializer(source='patient_id', read_only=True)
    
    class Meta:
        model = Rehabilitation_Plans
        fields = ['id', 'patient', 'clinician', 'start_date', 'end_date', 'current_cycle', 'goals', 'status']

class AssessmentMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment_Metrics
        fields = ['id', 'metric_name', 'unit', 'min_value', 'max_value']

class ProgressMetricValueSerializer(serializers.ModelSerializer):
    metric = AssessmentMetricSerializer(source='metric_id', read_only=True)
    
    class Meta:
        model = Progress_Metric_Values
        fields = ['id', 'metric', 'value']

class ProgressLogSerializer(serializers.ModelSerializer):
    metric_values = ProgressMetricValueSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Progress_Logs
        fields = ['id', 'plan_id', 'log_date', 'treatment_given', 'clinician_notes', 'created_by_name', 'metric_values']

class ClinicianAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinician_Availability
        fields = ['id', 'clinician_id', 'date', 'start_time', 'end_time', 'is_leave', 'reason']

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientProfileSerializer(source='patient_id', read_only=True)
    clinician = ClinicianProfileSerializer(source='clinician_id', read_only=True)
    
    class Meta:
        model = Appointments
        fields = ['id', 'patient', 'clinician', 'start_time', 'end_time', 'status', 'is_auto_scheduled']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'title', 'message', 'is_read', 'created_at']

# Aliases and restored serializers for core/views.py

class PatientRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username', 'email', 'password', 'phone']
        
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patients
        fields = '__all__'

class ClinicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinicians
        fields = '__all__'
        
from .models import Resource_Types, Resources, AI_Analytics, Clinical_Reports, Activity_Logs

class ResourceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource_Types
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resources
        fields = '__all__'

class AIAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AI_Analytics
        fields = '__all__'

class ClinicalReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinical_Reports
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity_Logs
        fields = '__all__'

