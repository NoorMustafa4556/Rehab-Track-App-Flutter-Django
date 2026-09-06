from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from .models import Users, Roles, Patients, Clinicians, Rehabilitation_Plans, Appointments, Progress_Logs, Progress_Metric_Values, Assessment_Metrics
from .decorators import portal_required

def portal_login(request):
    """
    Login view for Patients and Clinicians.
    Rejects Admins.
    """
    if request.user.is_authenticated:
        if request.user.role_id and request.user.role_id.role_name == 'Admin':
            return redirect('admin_dashboard')
        return redirect('portal_dashboard')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            if user.role_id and user.role_id.role_name == 'Admin':
                messages.error(request, 'Admins must log in through the Admin Panel.')
            else:
                login(request, user)
                return redirect('portal_dashboard')
        else:
            messages.error(request, 'Invalid username/email or password.')
            
    return render(request, 'portal/login.html')


def portal_register(request):
    """
    Public registration page strictly for Patients.
    """
    if request.user.is_authenticated:
        return redirect('portal_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'portal/register.html')
            
        if Users.objects.filter(username=username).exists() or Users.objects.filter(email=email).exists():
            messages.error(request, 'Username or Email already exists.')
            return render(request, 'portal/register.html')
            
        try:
            with transaction.atomic():
                patient_role = Roles.objects.get(role_name='Patient')
                user = Users.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role_id=patient_role
                )
                Patients.objects.create(user_id=user)
                
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('portal_login')
        except Roles.DoesNotExist:
            messages.error(request, 'System configuration error: Patient role missing.')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            
    return render(request, 'portal/register.html')


def portal_logout(request):
    logout(request)
    return redirect('portal_login')


from django.utils import timezone

@portal_required
def portal_dashboard(request):
    """
    Dashboard view with branching logic based on the user's role.
    """
    user_role = request.user.role_id.role_name
    
    if user_role == 'Patient':
        # PATIENT DASHBOARD LOGIC
        try:
            patient = Patients.objects.get(user_id=request.user)
        except Patients.DoesNotExist:
            messages.error(request, 'Patient profile not found.')
            return redirect('portal_login')
            
        
        # 1. Fetch active rehab plan
        active_plan = Rehabilitation_Plans.objects.filter(
            patient_id=patient, status='Active'
        ).first()
        
        # 2. Fetch upcoming appointment
        upcoming_appt = Appointments.objects.filter(
            patient_id=patient,
            start_time__gte=timezone.now(),
            status='Booked'
        ).order_by('start_time').first()
        
        # 3. Fetch recent progress summary (if plan exists)
        recent_logs = []
        if active_plan:
            recent_logs = Progress_Logs.objects.filter(plan_id=active_plan).order_by('-log_date')[:3]
            
        context = {
            'active_plan': active_plan,
            'upcoming_appt': upcoming_appt,
            'recent_logs': recent_logs,
        }
        return render(request, 'portal/dashboard_patient.html', context)
        
    elif user_role == 'Clinician':
        # CLINICIAN DASHBOARD LOGIC
        try:
            clinician = Clinicians.objects.get(user_id=request.user)
        except Clinicians.DoesNotExist:
            messages.error(request, 'Clinician profile not found.')
            return redirect('portal_login')
            
        
        # 1. Fetch assigned patient count
        assigned_plans = Rehabilitation_Plans.objects.filter(
            clinician_id=clinician, status='Active'
        )
        assigned_patient_count = assigned_plans.values('patient_id').distinct().count()
        
        # 2. Fetch today's appointments
        today = timezone.now().date()
        today_appts = Appointments.objects.filter(
            clinician_id=clinician,
            start_time__date=today,
            status='Booked'
        ).order_by('start_time')
        
        context = {
            'assigned_patient_count': assigned_patient_count,
            'today_appts': today_appts,
        }
        return render(request, 'portal/dashboard_clinician.html', context)
        
    else:
        # Fallback for unexpected role
        messages.error(request, "Unrecognized role for portal access.")
        return redirect('portal_logout')

@portal_required
def patient_rehab_plan(request):
    """
    Detailed view of a Patient's active rehabilitation plan and progress metrics.
    Only accessible by the Patient themselves.
    """
    if request.user.role_id.role_name != 'Patient':
        messages.error(request, "Only patients can view their rehab plan directly.")
        return redirect('portal_dashboard')
        
    try:
        patient = Patients.objects.get(user_id=request.user)
    except Patients.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('portal_login')
        
    # Fetch active rehab plan
    active_plan = Rehabilitation_Plans.objects.filter(
        patient_id=patient, status='Active'
    ).first()
    
    # Fetch related progress logs if a plan exists
    progress_logs = []
    chart_labels_json = "[]"
    chart_datasets_json = "[]"
    
    if active_plan:
        import json
        progress_logs = Progress_Logs.objects.filter(plan_id=active_plan).order_by('-log_date')
        
        # Data preparation for Chart.js (needs chronological order)
        chronological_logs = list(reversed(progress_logs))
        labels = [log.log_date.strftime("%b %d") for log in chronological_logs]
        
        metric_values_by_id = {}
        metric_objects_by_id = {}
        # Pre-fill with None arrays to support missing data points
        for log in chronological_logs:
            for pmv in log.metric_values.all():
                m_id = pmv.metric_id.id
                if m_id not in metric_values_by_id:
                    metric_values_by_id[m_id] = [None] * len(chronological_logs)
                    metric_objects_by_id[m_id] = pmv.metric_id
                    
        # Populate actual values
        for i, log in enumerate(chronological_logs):
            for pmv in log.metric_values.all():
                metric_values_by_id[pmv.metric_id.id][i] = pmv.value
                
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        datasets = []
        chart_scales = {
            'x': {
                'display': True,
                'title': {'display': True, 'text': 'Date'}
            }
        }
        
        for i, (m_id, data) in enumerate(metric_values_by_id.items()):
            metric = metric_objects_by_id[m_id]
            m_name = f"{metric.metric_name} ({metric.unit})"
            color = colors[i % len(colors)]
            axis_id = f"yAxis_{m_id}"
            
            datasets.append({
                'label': m_name,
                'data': data,
                'borderColor': color,
                'backgroundColor': color,
                'tension': 0.3,
                'spanGaps': True,
                'yAxisID': axis_id
            })
            
            # Setup dynamic Y-axis for this specific metric
            chart_scales[axis_id] = {
                'type': 'linear',
                'display': True,
                'position': 'left' if i % 2 == 0 else 'right',
                'title': {'display': True, 'text': m_name, 'color': color},
                'ticks': {'color': color},
                'grid': {'drawOnChartArea': (i == 0)} # Only draw grid lines for the first axis
            }
            if metric.min_value is not None:
                chart_scales[axis_id]['min'] = metric.min_value
            if metric.max_value is not None:
                chart_scales[axis_id]['max'] = metric.max_value
            
        chart_labels_json = json.dumps(labels)
        chart_datasets_json = json.dumps(datasets)
        chart_scales_json = json.dumps(chart_scales)
        
    context = {
        'active_plan': active_plan,
        'progress_logs': progress_logs,
        'chart_labels': chart_labels_json,
        'chart_datasets': chart_datasets_json,
        'chart_scales': chart_scales_json if 'chart_scales_json' in locals() else "{}"
    }
    return render(request, 'portal/rehab_plan.html', context)


# ==========================================
# PHASE 4: CLINICIAN FEATURES
# ==========================================

@portal_required
def clinician_patients_list(request):
    """
    List of patients assigned to the logged-in Clinician.
    """
    if request.user.role_id.role_name != 'Clinician':
        messages.error(request, "Only clinicians can view the patient list.")
        return redirect('portal_dashboard')
        
    clinician = Clinicians.objects.get(user_id=request.user)
    
    # Get all active or paused plans assigned to this clinician
    assigned_plans = Rehabilitation_Plans.objects.filter(
        clinician_id=clinician, status__in=['Active', 'Paused']
    ).select_related('patient_id__user_id')
    
    context = {
        'assigned_plans': assigned_plans
    }
    return render(request, 'portal/clinician_patients.html', context)


@portal_required
def clinician_patient_detail(request, patient_id):
    """
    Detailed view of a specific patient's rehab plan, scoped to the Clinician.
    """
    if request.user.role_id.role_name != 'Clinician':
        messages.error(request, "Only clinicians can view patient details.")
        return redirect('portal_dashboard')
        
    clinician = Clinicians.objects.get(user_id=request.user)
    
    # Verify this clinician is actually assigned to this patient's active or paused plan
    active_plan = Rehabilitation_Plans.objects.filter(
        clinician_id=clinician, 
        patient_id__id=patient_id, 
        status__in=['Active', 'Paused']
    ).first()
    
    if not active_plan:
        messages.error(request, "You are not assigned to an active/paused plan for this patient.")
        return redirect('portal_patients_list')
        
    all_metrics = Assessment_Metrics.objects.all()
        
    if request.method == 'POST':
        treatment_given = request.POST.get('treatment_given')
        clinician_notes = request.POST.get('clinician_notes', '')
        
        if treatment_given:
            with transaction.atomic():
                log = Progress_Logs.objects.create(
                    plan_id=active_plan,
                    log_date=timezone.now().date(),
                    treatment_given=treatment_given,
                    clinician_notes=clinician_notes,
                    created_by=request.user
                )
                
                for metric in all_metrics:
                    metric_val = request.POST.get(f'metric_{metric.id}')
                    if metric_val:
                        Progress_Metric_Values.objects.create(
                            log_id=log,
                            metric_id=metric,
                            value=float(metric_val)
                        )
                messages.success(request, "Progress Log added successfully.")
            return redirect('portal_patient_detail', patient_id=patient_id)
        else:
            messages.error(request, "Treatment given is required.")
        
    import json
    progress_logs = Progress_Logs.objects.filter(plan_id=active_plan).order_by('-log_date')
    
    # Reusing the same chart logic as patient_rehab_plan
    chart_labels_json = "[]"
    chart_datasets_json = "[]"
    chart_scales_json = "{}"
    
    if progress_logs.exists():
        chronological_logs = list(reversed(progress_logs))
        labels = [log.log_date.strftime("%b %d") for log in chronological_logs]
        
        metric_values_by_id = {}
        metric_objects_by_id = {}
        for log in chronological_logs:
            for pmv in log.metric_values.all():
                m_id = pmv.metric_id.id
                if m_id not in metric_values_by_id:
                    metric_values_by_id[m_id] = [None] * len(chronological_logs)
                    metric_objects_by_id[m_id] = pmv.metric_id
                    
        for i, log in enumerate(chronological_logs):
            for pmv in log.metric_values.all():
                metric_values_by_id[pmv.metric_id.id][i] = pmv.value
                
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        datasets = []
        chart_scales = {
            'x': {'display': True, 'title': {'display': True, 'text': 'Date'}}
        }
        
        for i, (m_id, data) in enumerate(metric_values_by_id.items()):
            metric = metric_objects_by_id[m_id]
            m_name = f"{metric.metric_name} ({metric.unit})"
            color = colors[i % len(colors)]
            axis_id = f"yAxis_{m_id}"
            
            datasets.append({
                'label': m_name, 'data': data, 'borderColor': color,
                'backgroundColor': color, 'tension': 0.3, 'spanGaps': True, 'yAxisID': axis_id
            })
            
            chart_scales[axis_id] = {
                'type': 'linear', 'display': True, 'position': 'left' if i % 2 == 0 else 'right',
                'title': {'display': True, 'text': m_name, 'color': color},
                'ticks': {'color': color}, 'grid': {'drawOnChartArea': (i == 0)}
            }
            if metric.min_value is not None: chart_scales[axis_id]['min'] = metric.min_value
            if metric.max_value is not None: chart_scales[axis_id]['max'] = metric.max_value
            
        chart_labels_json = json.dumps(labels)
        chart_datasets_json = json.dumps(datasets)
        chart_scales_json = json.dumps(chart_scales)
    
    context = {
        'active_plan': active_plan,
        'patient': active_plan.patient_id,
        'progress_logs': progress_logs,
        'chart_labels': chart_labels_json,
        'chart_datasets': chart_datasets_json,
        'chart_scales': chart_scales_json,
        'all_metrics': all_metrics
    }
    return render(request, 'portal/clinician_patient_detail.html', context)


@portal_required
def clinician_availability(request):
    """
    View and manage Clinician availability.
    """
    if request.user.role_id.role_name != 'Clinician':
        messages.error(request, "Only clinicians can manage availability.")
        return redirect('portal_dashboard')
        
    clinician = Clinicians.objects.get(user_id=request.user)
    
    from .models import Clinician_Availability
    
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        action = request.POST.get('action')
        
        if slot_id and action:
            try:
                slot = Clinician_Availability.objects.get(id=slot_id, clinician_id=clinician)
                if action == 'mark_leave':
                    slot.is_leave = True
                    slot.reason = "Marked on leave via portal"
                    
                    # Automatic Notification to all active patients
                    from .models import Rehabilitation_Plans, Notifications
                    active_patients = Rehabilitation_Plans.objects.filter(
                        clinician_id=clinician, status='Active'
                    ).select_related('patient_id__user_id')
                    
                    for plan in active_patients:
                        Notifications.objects.create(
                            user_id=plan.patient_id.user_id,
                            title="Clinician Leave Notice",
                            message=f"Dr. {request.user.username} will be on leave on {slot.date.strftime('%b %d, %Y')}. Any appointments on this day will be rescheduled."
                        )
                        
                elif action == 'mark_available':
                    slot.is_leave = False
                    slot.reason = ""
                slot.save()
                messages.success(request, 'Availability updated successfully.')
            except Clinician_Availability.DoesNotExist:
                messages.error(request, 'Invalid availability slot.')
        return redirect('portal_availability')
        
    today = timezone.now().date()
    # Get upcoming 14 days of availability
    schedule = Clinician_Availability.objects.filter(
        clinician_id=clinician,
        date__gte=today
    ).order_by('date')
    
    context = {
        'schedule': schedule
    }
    return render(request, 'portal/availability.html', context)


# ==========================================
# PHASE 5: SHARED FEATURES (Appointments & Notifications)
# ==========================================

@portal_required
def portal_notifications(request):
    from .models import Notifications
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            Notifications.objects.filter(user_id=request.user, is_read=False).update(is_read=True)
            messages.success(request, 'All notifications marked as read.')
        elif action == 'mark_read':
            notif_id = request.POST.get('notif_id')
            if notif_id:
                Notifications.objects.filter(id=notif_id, user_id=request.user).update(is_read=True)
        return redirect('portal_notifications')
        
    user_notifications = Notifications.objects.filter(user_id=request.user).order_by('-created_at')
    
    context = {
        'user_notifications': user_notifications
    }
    return render(request, 'portal/notifications.html', context)

@portal_required
def portal_appointments(request):
    from .models import Appointments, Clinicians, Patients, Clinician_Availability, Rehabilitation_Plans, Notifications
    import datetime
    
    user_role = request.user.role_id.role_name
    
    if request.method == 'POST':
        if user_role == 'Patient':
            # Handle Book New Appointment
            appt_date_str = request.POST.get('date')
            appt_time_str = request.POST.get('time')
            
            if not appt_date_str or not appt_time_str:
                messages.error(request, "Date and Time are required.")
                return redirect('portal_appointments')
                
            appt_date = datetime.datetime.strptime(appt_date_str, '%Y-%m-%d').date()
            appt_time = datetime.datetime.strptime(appt_time_str, '%H:%M').time()
            
            # Combine to aware datetime
            appt_datetime = timezone.make_aware(datetime.datetime.combine(appt_date, appt_time))
            appt_end_datetime = appt_datetime + datetime.timedelta(hours=1)
            
            # Identify clinician from active plan
            patient = Patients.objects.get(user_id=request.user)
            active_plan = Rehabilitation_Plans.objects.filter(patient_id=patient, status='Active').first()
            if not active_plan:
                messages.error(request, "You need an active rehab plan to book an appointment.")
                return redirect('portal_appointments')
                
            clinician = active_plan.clinician_id
            
            # Validation 1: Clinician Availability (is_leave)
            leave_slot = Clinician_Availability.objects.filter(clinician_id=clinician, date=appt_date, is_leave=True).exists()
            if leave_slot:
                messages.error(request, f"Dr. {clinician.user_id.username} is on leave on {appt_date_str}. Please choose another date.")
                return redirect('portal_appointments')
                
            # Validation 2: Double-Booking Check (Overlapping ranges)
            # new_start < existing_end AND new_end > existing_start
            from django.db.models import Q
            clash = Appointments.objects.filter(
                clinician_id=clinician,
                status__in=['Booked', 'In Progress']
            ).filter(
                Q(start_time__lt=appt_end_datetime) & Q(end_time__gt=appt_datetime)
            ).exists()
            
            if clash:
                messages.error(request, f"The selected time slot is already booked. Please choose another time.")
                return redirect('portal_appointments')
                
            # Create Appointment
            with transaction.atomic():
                appt = Appointments.objects.create(
                    patient_id=patient,
                    clinician_id=clinician,
                    resource_id=None, # Portal doesn't manage physical resources
                    start_time=appt_datetime,
                    end_time=appt_datetime + datetime.timedelta(hours=1),
                    status='Booked'
                )
                
                # Automatic Event-Triggered Notification to Clinician
                Notifications.objects.create(
                    user_id=clinician.user_id,
                    title="New Appointment Booked",
                    message=f"Patient {request.user.username} has booked an appointment for {appt_date_str} at {appt_time_str}."
                )
                
            messages.success(request, "Appointment booked successfully!")
            return redirect('portal_appointments')
            
        elif user_role == 'Clinician':
            # Handle Update Appointment Status
            appt_id = request.POST.get('appt_id')
            new_status = request.POST.get('status')
            
            if appt_id and new_status:
                try:
                    clinician = Clinicians.objects.get(user_id=request.user)
                    appt = Appointments.objects.get(id=appt_id, clinician_id=clinician)
                    
                    old_status = appt.status
                    appt.status = new_status
                    appt.save()
                    
                    # Automatic Event-Triggered Notification to Patient on Cancel/Reschedule
                    if new_status in ['Cancelled', 'Rescheduled']:
                        Notifications.objects.create(
                            user_id=appt.patient_id.user_id,
                            title=f"Appointment {new_status}",
                            message=f"Dr. {request.user.username} has updated the status of your appointment on {appt.start_time.strftime('%b %d, %Y')} to {new_status}."
                        )
                    
                    messages.success(request, f"Appointment status updated to {new_status}.")
                except Appointments.DoesNotExist:
                    messages.error(request, "Invalid appointment.")
            return redirect('portal_appointments')
            
    # GET Logic
    if user_role == 'Patient':
        patient = Patients.objects.get(user_id=request.user)
        upcoming = Appointments.objects.filter(patient_id=patient, start_time__gte=timezone.now(), status='Booked').order_by('start_time')
        past = Appointments.objects.filter(patient_id=patient, start_time__lt=timezone.now()).order_by('-start_time')
        context = {
            'upcoming': upcoming,
            'past': past,
            'role': 'Patient'
        }
    elif user_role == 'Clinician':
        clinician = Clinicians.objects.get(user_id=request.user)
        upcoming = Appointments.objects.filter(clinician_id=clinician, start_time__gte=timezone.now(), status__in=['Booked', 'In Progress']).order_by('start_time')
        past = Appointments.objects.filter(clinician_id=clinician, start_time__lt=timezone.now()).order_by('-start_time')
        context = {
            'upcoming': upcoming,
            'past': past,
            'role': 'Clinician'
        }
    else:
        return redirect('portal_dashboard')
        
    return render(request, 'portal/appointments.html', context)

# ==========================================
# PHASE 6: CLINICAL REPORTING (PDFs)
# ==========================================

@portal_required
def generate_clinical_report(request, plan_id):
    from .models import Rehabilitation_Plans, Progress_Logs, Clinical_Reports, Assessment_Metrics, Progress_Metric_Values
    from django.template.loader import get_template
    from django.http import HttpResponse
    from xhtml2pdf import pisa
    import io
    
    # Verify permission: Must be the clinician assigned to this plan OR the patient themselves
    user = request.user
    role = user.role_id.role_name
    
    plan = Rehabilitation_Plans.objects.filter(id=plan_id).first()
    if not plan:
        messages.error(request, "Rehab plan not found.")
        return redirect('portal_dashboard')
        
    # Access Control Logic
    is_authorized = False
    if role == 'Clinician' and plan.clinician_id and plan.clinician_id.user_id == user:
        is_authorized = True
    elif role == 'Patient' and plan.patient_id and plan.patient_id.user_id == user:
        is_authorized = True
        
    if not is_authorized:
        messages.error(request, "Unauthorized access to this report.")
        return redirect('portal_dashboard')
        
    logs = Progress_Logs.objects.filter(plan_id=plan).order_by('log_date')
    all_metrics = Assessment_Metrics.objects.all()
    
    # Calculate initial vs current metrics
    metric_summary = []
    if logs.exists():
        first_log = logs.first()
        last_log = logs.last()
        
        for metric in all_metrics:
            initial = Progress_Metric_Values.objects.filter(log_id=first_log, metric_id=metric).first()
            current = Progress_Metric_Values.objects.filter(log_id=last_log, metric_id=metric).first()
            if initial or current:
                net_change = 0
                if initial and current:
                    net_change = round(current.value - initial.value, 2)
                    
                metric_summary.append({
                    'name': metric.metric_name,
                    'unit': metric.unit,
                    'initial': initial.value if initial else 'N/A',
                    'current': current.value if current else 'N/A',
                    'net_change': net_change
                })
                
    # Save a record in Clinical_Reports
    with transaction.atomic():
        report = Clinical_Reports.objects.create(
            plan_id=plan,
            cycle_number=plan.current_cycle,
            summary=f"Report generated automatically. Logs count: {logs.count()}"
        )
        
    context = {
        'plan': plan,
        'patient': plan.patient_id,
        'logs': logs,
        'metric_summary': metric_summary,
        'report_date': timezone.now().date(),
        'report_id': report.id
    }
    
    template = get_template('portal/pdf_report.html')
    html_content = template.render(context)
    
    # Generate PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Clinical_Report_{plan.patient_id.user_id.username}_{timezone.now().strftime("%Y%m%d")}.pdf"'
        return response
    else:
        messages.error(request, "Error generating PDF report.")
        return redirect('portal_patient_detail', patient_id=plan.patient_id.id)
