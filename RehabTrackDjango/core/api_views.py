from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import datetime

from .models import (
    Users, Patients, Clinicians, Rehabilitation_Plans,
    Progress_Logs, Progress_Metric_Values, Assessment_Metrics,
    Appointments, Clinician_Availability, Notifications
)
from .serializers import (
    UserSerializer, PatientProfileSerializer, ClinicianProfileSerializer,
    RehabilitationPlanSerializer, ProgressLogSerializer,
    ClinicianAvailabilitySerializer, AppointmentSerializer, NotificationSerializer,
    AssessmentMetricSerializer
)

# ==========================================
# AUTH & PROFILE
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register_patient(request):
    from django.contrib.auth.hashers import make_password
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if Users.objects.filter(username=username).exists():
        return Response({'username': ['Username already exists.']}, status=status.HTTP_400_BAD_REQUEST)

    patient_role = Roles.objects.filter(role_name='Patient').first()
    if not patient_role:
        return Response({'detail': 'System configuration error. Patient role not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user = Users.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        role_id=patient_role
    )
    
    # Also create the Patient profile
    Patients.objects.create(user_id=user)

    return Response({'detail': 'Account created successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    """Returns the profile of the currently logged-in user based on their role."""
    user = request.user
    role_name = user.role_id.role_name
    
    if role_name == 'Patient':
        patient = Patients.objects.filter(user_id=user).first()
        serializer = PatientProfileSerializer(patient)
        return Response({'role': role_name, 'profile': serializer.data})
    elif role_name == 'Clinician':
        clinician = Clinicians.objects.filter(user_id=user).first()
        serializer = ClinicianProfileSerializer(clinician)
        return Response({'role': role_name, 'profile': serializer.data})
    else:
        serializer = UserSerializer(user)
        return Response({'role': role_name, 'profile': serializer.data})

# ==========================================
# PATIENT APIS
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_plan(request):
    try:
        patient = Patients.objects.get(user_id=request.user)
    except Patients.DoesNotExist:
        return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
    active_plan = Rehabilitation_Plans.objects.filter(patient_id=patient, status='Active').first()
    if not active_plan:
        return Response({"error": "No active rehabilitation plan found."}, status=status.HTTP_404_NOT_FOUND)
        
    serializer = RehabilitationPlanSerializer(active_plan)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_progress(request):
    patient = Patients.objects.filter(user_id=request.user).first()
    active_plan = Rehabilitation_Plans.objects.filter(patient_id=patient, status='Active').first()
    if not active_plan:
        return Response([])
        
    logs = Progress_Logs.objects.filter(plan_id=active_plan).order_by('-log_date')
    serializer = ProgressLogSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def patient_appointments(request):
    patient = Patients.objects.filter(user_id=request.user).first()
    
    if request.method == 'GET':
        upcoming = Appointments.objects.filter(patient_id=patient, start_time__gte=timezone.now(), status='Booked').order_by('start_time')
        past = Appointments.objects.filter(patient_id=patient, start_time__lt=timezone.now()).order_by('-start_time')
        return Response({
            'upcoming': AppointmentSerializer(upcoming, many=True).data,
            'past': AppointmentSerializer(past, many=True).data
        })
        
    elif request.method == 'POST':
        appt_date_str = request.data.get('date')
        appt_time_str = request.data.get('time')
        
        if not appt_date_str or not appt_time_str:
            return Response({"error": "date and time are required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            appt_date = datetime.datetime.strptime(appt_date_str, '%Y-%m-%d').date()
            appt_time = datetime.datetime.strptime(appt_time_str, '%H:%M').time()
        except ValueError:
            return Response({"error": "Invalid date/time format. Use YYYY-MM-DD and HH:MM."}, status=status.HTTP_400_BAD_REQUEST)
            
        appt_datetime = timezone.make_aware(datetime.datetime.combine(appt_date, appt_time))
        appt_end_datetime = appt_datetime + datetime.timedelta(hours=1)
        
        active_plan = Rehabilitation_Plans.objects.filter(patient_id=patient, status='Active').first()
        if not active_plan:
            return Response({"error": "Active rehab plan required."}, status=status.HTTP_403_FORBIDDEN)
            
        clinician = active_plan.clinician_id
        
        # Validation 1: Leave
        if Clinician_Availability.objects.filter(clinician_id=clinician, date=appt_date, is_leave=True).exists():
            return Response({"error": "Clinician is on leave on this date."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Validation 2: Double-Booking
        clash = Appointments.objects.filter(
            clinician_id=clinician, status__in=['Booked', 'In Progress']
        ).filter(
            Q(start_time__lt=appt_end_datetime) & Q(end_time__gt=appt_datetime)
        ).exists()
        
        if clash:
            return Response({"error": "Time slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            appt = Appointments.objects.create(
                patient_id=patient, clinician_id=clinician,
                start_time=appt_datetime, end_time=appt_end_datetime,
                status='Booked'
            )
            Notifications.objects.create(
                user_id=clinician.user_id, title="New Appointment",
                message=f"Patient {request.user.username} booked {appt_date_str} at {appt_time_str}."
            )
            
        return Response(AppointmentSerializer(appt).data, status=status.HTTP_201_CREATED)

# ==========================================
# CLINICIAN APIS
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clinician_patients(request):
    clinician = Clinicians.objects.filter(user_id=request.user).first()
    if not clinician:
        return Response({"error": "Not a clinician."}, status=status.HTTP_403_FORBIDDEN)
        
    plans = Rehabilitation_Plans.objects.filter(clinician_id=clinician, status__in=['Active', 'Paused'])
    serializer = RehabilitationPlanSerializer(plans, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clinician_patient_detail(request, patient_id):
    clinician = Clinicians.objects.filter(user_id=request.user).first()
    plan = Rehabilitation_Plans.objects.filter(clinician_id=clinician, patient_id__id=patient_id, status__in=['Active', 'Paused']).first()
    
    if not plan:
        return Response({"error": "Not assigned to this patient's active/paused plan."}, status=status.HTTP_403_FORBIDDEN)
        
    logs = Progress_Logs.objects.filter(plan_id=plan).order_by('-log_date')
    metrics = Assessment_Metrics.objects.all()
    
    return Response({
        'plan': RehabilitationPlanSerializer(plan).data,
        'logs': ProgressLogSerializer(logs, many=True).data,
        'available_metrics': AssessmentMetricSerializer(metrics, many=True).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clinician_progress_add(request, patient_id):
    clinician = Clinicians.objects.filter(user_id=request.user).first()
    plan = Rehabilitation_Plans.objects.filter(clinician_id=clinician, patient_id__id=patient_id, status__in=['Active', 'Paused']).first()
    
    if not plan:
        return Response({"error": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        
    treatment_given = request.data.get('treatment_given')
    clinician_notes = request.data.get('clinician_notes', '')
    metrics_data = request.data.get('metrics', {}) # expects dict {metric_id: value}
    
    if not treatment_given:
        return Response({"error": "treatment_given is required."}, status=status.HTTP_400_BAD_REQUEST)
        
    with transaction.atomic():
        log = Progress_Logs.objects.create(
            plan_id=plan, log_date=timezone.now().date(),
            treatment_given=treatment_given, clinician_notes=clinician_notes,
            created_by=request.user
        )
        for m_id, val in metrics_data.items():
            metric = Assessment_Metrics.objects.get(id=m_id)
            Progress_Metric_Values.objects.create(log_id=log, metric_id=metric, value=float(val))
            
    return Response(ProgressLogSerializer(log).data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def clinician_availability(request):
    clinician = Clinicians.objects.filter(user_id=request.user).first()
    
    if request.method == 'GET':
        slots = Clinician_Availability.objects.filter(clinician_id=clinician, date__gte=timezone.now().date()).order_by('date')
        return Response(ClinicianAvailabilitySerializer(slots, many=True).data)
        
    elif request.method == 'POST':
        slot_id = request.data.get('slot_id')
        action = request.data.get('action') # 'mark_leave' or 'mark_available'
        
        try:
            slot = Clinician_Availability.objects.get(id=slot_id, clinician_id=clinician)
            if action == 'mark_leave':
                slot.is_leave = True
                slot.reason = "Marked via App"
                
                # Notify patients
                active_plans = Rehabilitation_Plans.objects.filter(clinician_id=clinician, status='Active')
                for plan in active_plans:
                    Notifications.objects.create(
                        user_id=plan.patient_id.user_id,
                        title="Clinician Leave Notice",
                        message=f"Dr. {request.user.username} will be on leave on {slot.date}."
                    )
            elif action == 'mark_available':
                slot.is_leave = False
                slot.reason = ""
            slot.save()
            return Response(ClinicianAvailabilitySerializer(slot).data)
        except Clinician_Availability.DoesNotExist:
            return Response({"error": "Invalid slot."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def clinician_appointments(request):
    clinician = Clinicians.objects.filter(user_id=request.user).first()
    
    if request.method == 'GET':
        upcoming = Appointments.objects.filter(clinician_id=clinician, start_time__gte=timezone.now(), status__in=['Booked', 'In Progress']).order_by('start_time')
        past = Appointments.objects.filter(clinician_id=clinician, start_time__lt=timezone.now()).order_by('-start_time')
        return Response({
            'upcoming': AppointmentSerializer(upcoming, many=True).data,
            'past': AppointmentSerializer(past, many=True).data
        })
        
    elif request.method == 'POST':
        appt_id = request.data.get('appt_id')
        new_status = request.data.get('status')
        
        try:
            appt = Appointments.objects.get(id=appt_id, clinician_id=clinician)
            appt.status = new_status
            appt.save()
            
            if new_status in ['Cancelled', 'Rescheduled']:
                Notifications.objects.create(
                    user_id=appt.patient_id.user_id, title=f"Appointment {new_status}",
                    message=f"Your appointment was marked as {new_status}."
                )
            return Response(AppointmentSerializer(appt).data)
        except Appointments.DoesNotExist:
            return Response({"error": "Invalid appointment."}, status=status.HTTP_404_NOT_FOUND)

# ==========================================
# SHARED APIS
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notifications(request):
    if request.method == 'GET':
        notifs = Notifications.objects.filter(user_id=request.user).order_by('-created_at')
        return Response(NotificationSerializer(notifs, many=True).data)
        
    elif request.method == 'POST':
        notif_id = request.data.get('notif_id')
        action = request.data.get('action') # 'mark_read' or 'mark_all_read'
        
        if action == 'mark_all_read':
            Notifications.objects.filter(user_id=request.user, is_read=False).update(is_read=True)
        elif action == 'mark_read' and notif_id:
            Notifications.objects.filter(id=notif_id, user_id=request.user).update(is_read=True)
            
        return Response({"success": True})
