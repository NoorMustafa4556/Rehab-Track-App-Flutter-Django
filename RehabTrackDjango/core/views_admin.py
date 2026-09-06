from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Patients, Clinicians, Rehabilitation_Plans, Appointments, Resources, AI_Analytics, Activity_Logs, Clinical_Reports, Users, Roles
from .decorators import admin_required
import json

def log_action(request, action, description):
    """Helper: write an Activity_Log entry for any admin action."""
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        Activity_Logs.objects.create(
            user_id=request.user,
            action=action,
            description=description,
            ip_address=ip or '127.0.0.1'
        )
    except Exception:
        pass  # Never let logging break the main request

def admin_login(request):
    if request.user.is_authenticated and request.user.role_id and request.user.role_id.role_name == 'Admin':
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            if user.role_id and user.role_id.role_name == 'Admin':
                login(request, user)
                log_action(request, 'ADMIN_LOGIN', f'Admin {user.username} logged in to admin panel')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. You must be an Admin.')
        else:
            messages.error(request, 'Invalid credentials.')
            
    return render(request, 'admin_panel/login.html')

def admin_logout(request):
    if request.user.is_authenticated:
        log_action(request, 'ADMIN_LOGOUT', f'{request.user.username} logged out')
    logout(request)
    return redirect('admin_login')

@admin_required
def dashboard(request):
    total_patients = Patients.objects.filter(deleted_at__isnull=True).count()
    total_clinicians = Clinicians.objects.count()
    active_plans = Rehabilitation_Plans.objects.filter(status='Active').count()
    today_appointments = Appointments.objects.filter(start_time__date=timezone.now().date()).count()
    
    # Resources utilization
    total_resources = Resources.objects.filter(deleted_at__isnull=True).count()
    available_resources = Resources.objects.filter(is_available=True, deleted_at__isnull=True).count()
    in_use_resources = total_resources - available_resources
    
    # Plateau risk alerts
    high_risk_analytics = AI_Analytics.objects.filter(plateau_risk_score__gte=7.0).select_related('plan_id__patient_id__user_id')[:5]
    
    # Appointments trend: last 7 days
    from django.db.models import Count
    from datetime import timedelta, date
    today = timezone.now().date()
    appt_labels = []
    appt_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Appointments.objects.filter(start_time__date=day).count()
        appt_labels.append(day.strftime('%b %d'))
        appt_data.append(count)
    
    total_appointments_last_7_days = sum(appt_data)
    
    context = {
        'total_patients': total_patients,
        'total_clinicians': total_clinicians,
        'active_plans': active_plans,
        'today_appointments': today_appointments,
        'available_resources': available_resources,
        'in_use_resources': in_use_resources,
        'high_risk_analytics': high_risk_analytics,
        'total_appointments_last_7_days': total_appointments_last_7_days,
        # Chart Data
        'resource_chart_data': json.dumps({
            'labels': ['Available', 'In Use'],
            'data': [available_resources, in_use_resources]
        }),
        'appointments_chart_data': json.dumps({
            'labels': appt_labels,
            'data': appt_data
        }),
    }
    return render(request, 'admin_panel/dashboard.html', context)

@admin_required
def activity_logs(request):
    logs_list = Activity_Logs.objects.select_related('user_id').order_by('-timestamp')
    
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs_list = logs_list.filter(action__icontains=action_filter)
        
    paginator = Paginator(logs_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/activity_logs.html', {'page_obj': page_obj, 'action_filter': action_filter})

@admin_required
def reports_viewer(request):
    reports_list = Clinical_Reports.objects.select_related('plan_id__patient_id__user_id').order_by('-generated_at')
    
    paginator = Paginator(reports_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/reports.html', {'page_obj': page_obj})

from django.db import transaction
from django.contrib.auth.hashers import make_password

@admin_required
def users_management(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role_id_val = request.POST.get('role_id')
        
        try:
            role = Roles.objects.get(id=role_id_val)
            with transaction.atomic():
                new_user = Users.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password),
                    role_id=role
                )
                if role.role_name == 'Clinician':
                    Clinicians.objects.create(user_id=new_user)
                elif role.role_name == 'Patient':
                    Patients.objects.create(user_id=new_user)
            messages.success(request, f"User {username} created successfully!")
            log_action(request, 'USER_CREATED', f'Created {role.role_name} account: {username} ({email})')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            
        return redirect('admin_users')
        
    users_list = Users.objects.select_related('role_id').order_by('-date_joined')
    roles = Roles.objects.all()
    
    paginator = Paginator(users_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/users.html', {'page_obj': page_obj, 'roles': roles})

@admin_required
def clinicians_management(request):
    clinicians_list = Clinicians.objects.select_related('user_id', 'specialization_id')
    
    paginator = Paginator(clinicians_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/clinicians.html', {'page_obj': page_obj})

@admin_required
def patients_management(request):
    patients_list = Patients.objects.select_related('user_id').filter(deleted_at__isnull=True).order_by('-created_at')
    
    search_q = request.GET.get('search', '')
    if search_q:
        patients_list = patients_list.filter(user_id__username__icontains=search_q)
        
    paginator = Paginator(patients_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/patients.html', {'page_obj': page_obj, 'search_q': search_q})

from django.http import JsonResponse

@admin_required
def delete_patient(request, patient_id):
    if request.method == 'POST':
        try:
            patient = Patients.objects.get(id=patient_id)
            patient.deleted_at = timezone.now()
            patient.save()
            log_action(request, 'PATIENT_DELETED', f'Soft-deleted patient: {patient.user_id.username} (ID: {patient_id})')
            return JsonResponse({'success': True})
        except Patients.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Patient not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

from .models import Resource_Types

@admin_required
def appointments_management(request):
    appointments_list = Appointments.objects.select_related('patient_id__user_id', 'clinician_id__user_id', 'resource_id').order_by('-start_time')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments_list = appointments_list.filter(status=status_filter)
        
    paginator = Paginator(appointments_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/appointments.html', {'page_obj': page_obj, 'status_filter': status_filter})

@admin_required
def resources_management(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        type_id_val = request.POST.get('type_id')
        try:
            resource_type = Resource_Types.objects.get(id=type_id_val)
            Resources.objects.create(name=name, type_id=resource_type)
            messages.success(request, f"Resource {name} added successfully.")
            log_action(request, 'RESOURCE_ADDED', f'Added resource: {name} (Type: {resource_type.name})')
        except Exception as e:
            messages.error(request, f"Error adding resource: {str(e)}")
        return redirect('admin_resources')
        
    resources_list = Resources.objects.select_related('type_id').filter(deleted_at__isnull=True).order_by('name')
    resource_types = Resource_Types.objects.all()
    
    return render(request, 'admin_panel/resources.html', {'resources_list': resources_list, 'resource_types': resource_types})

@admin_required
def delete_resource(request, resource_id):
    if request.method == 'POST':
        try:
            resource = Resources.objects.get(id=resource_id)
            resource.deleted_at = timezone.now()
            resource.save()
            log_action(request, 'RESOURCE_DELETED', f'Soft-deleted resource: {resource.name} (ID: {resource_id})')
            return JsonResponse({'success': True})
        except Resources.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Resource not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

from .models import Specializations, Assessment_Metrics

@admin_required
def system_lookups(request):
    if request.method == 'POST':
        lookup_type = request.POST.get('lookup_type')
        if lookup_type == 'specialization':
            name = request.POST.get('name')
            Specializations.objects.create(name=name)
            messages.success(request, f"Specialization '{name}' added.")
            log_action(request, 'LOOKUP_ADDED', f'Added Specialization: {name}')
        elif lookup_type == 'resource_type':
            name = request.POST.get('type_name')
            Resource_Types.objects.create(name=name)
            messages.success(request, f"Resource Type '{name}' added.")
            log_action(request, 'LOOKUP_ADDED', f'Added Resource Type: {name}')
        elif lookup_type == 'assessment_metric':
            name = request.POST.get('metric_name')
            Assessment_Metrics.objects.create(metric_name=name)
            messages.success(request, f"Assessment Metric '{name}' added.")
            log_action(request, 'LOOKUP_ADDED', f'Added Assessment Metric: {name}')
        return redirect('admin_lookups')

    context = {
        'roles': Roles.objects.all(),
        'specializations': Specializations.objects.all(),
        'resource_types': Resource_Types.objects.all().values('id', 'name'),
        'metrics': Assessment_Metrics.objects.all(),
    }
    return render(request, 'admin_panel/system_lookups.html', context)

@admin_required
def delete_lookup(request, lookup_type, lookup_id):
    if request.method == 'POST':
        try:
            if lookup_type == 'specialization':
                obj = Specializations.objects.get(id=lookup_id)
                count = Clinicians.objects.filter(specialization_id=obj).count()
                if count > 0:
                    return JsonResponse({'success': False, 'error': f'Cannot delete: {count} Clinicians are currently linked to this Specialization.'})
                obj.delete()
                
            elif lookup_type == 'resource_type':
                obj = Resource_Types.objects.get(id=lookup_id)
                count = Resources.objects.filter(type_id=obj).count()
                if count > 0:
                    return JsonResponse({'success': False, 'error': f'Cannot delete: {count} Resources are currently linked to this Resource Type.'})
                obj.delete()
                
            elif lookup_type == 'assessment_metric':
                obj = Assessment_Metrics.objects.get(id=lookup_id)
                from .models import Progress_Metric_Values
                count = Progress_Metric_Values.objects.filter(metric_id=obj).count()
                if count > 0:
                    return JsonResponse({'success': False, 'error': f'Cannot delete: {count} clinical progress records use this Metric.'})
                obj.delete()
                
            else:
                return JsonResponse({'success': False, 'error': 'Invalid lookup type.'})
                
            log_action(request, 'LOOKUP_DELETED', f'Deleted {lookup_type} (ID: {lookup_id})')
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

from django.shortcuts import get_object_or_404

@admin_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patients, id=patient_id)
    
    if request.method == 'POST':
        clinician_id = request.POST.get('clinician_id')
        goals = request.POST.get('goals')
        start_date = request.POST.get('start_date')
        
        try:
            clinician = Clinicians.objects.get(id=clinician_id)
            Rehabilitation_Plans.objects.create(
                patient_id=patient,
                clinician_id=clinician,
                goals=goals,
                start_date=start_date,
                status='Active'
            )
            messages.success(request, 'New Rehabilitation Plan created and cycle initiated.')
            log_action(request, 'REHAB_PLAN_CREATED', f'Created Rehab Plan for patient: {patient.user_id.username}, clinician: {clinician.user_id.username}')
        except Exception as e:
            messages.error(request, f'Error creating plan: {str(e)}')
            
        return redirect('admin_patient_detail', patient_id=patient.id)
        
    plans = Rehabilitation_Plans.objects.filter(patient_id=patient).order_by('-start_date')
    clinicians = Clinicians.objects.select_related('user_id').all()
    
    context = {
        'patient': patient,
        'plans': plans,
        'clinicians': clinicians
    }
    return render(request, 'admin_panel/patient_detail.html', context)

@admin_required
def clinician_detail(request, clinician_id):
    clinician = get_object_or_404(Clinicians, id=clinician_id)
    
    if request.method == 'POST':
        is_available = request.POST.get('is_available') == 'on'
        working_hours = request.POST.get('working_hours')
        
        clinician.is_available = is_available
        if working_hours:
            clinician.working_hours = working_hours
        clinician.save()
        messages.success(request, 'Clinician availability overridden.')
        log_action(request, 'CLINICIAN_UPDATED', f'Overrode availability for clinician: {clinician.user_id.username} → is_available={is_available}')
        return redirect('admin_clinician_detail', clinician_id=clinician.id)
        
    plans = Rehabilitation_Plans.objects.filter(clinician_id=clinician, status='Active')
    
    context = {
        'clinician': clinician,
        'active_plans': plans
    }
    return render(request, 'admin_panel/clinician_detail.html', context)

from .models import Permissions, Role_Permissions

@admin_required
def role_permissions_view(request):
    if not request.user.has_permission('can_manage_permissions'):
        messages.error(request, "You do not have permission to manage roles and permissions.")
        return redirect('admin_dashboard')

    roles = Roles.objects.all()
    # Group permissions by module
    permissions_list = Permissions.objects.all()
    modules = {}
    for perm in permissions_list:
        modules.setdefault(perm.module, []).append(perm)

    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        role = get_object_or_404(Roles, id=role_id)
        
        # Get checked permissions from the form
        selected_perm_ids = request.POST.getlist('permissions')
        selected_perm_ids = [int(pid) for pid in selected_perm_ids]
        
        # Self-lockout protection for Admin role
        if role.role_name == 'Admin':
            # Find IDs of critical permissions
            try:
                admin_panel_perm_id = Permissions.objects.get(permission_name='can_access_admin_panel').id
                manage_perms_perm_id = Permissions.objects.get(permission_name='can_manage_permissions').id
                
                if admin_panel_perm_id not in selected_perm_ids or manage_perms_perm_id not in selected_perm_ids:
                    messages.error(request, "Cannot remove critical permissions (access admin panel, manage permissions) from the Admin role — it would lock all Admins out of the system.")
                    return redirect('admin_role_permissions')
            except Permissions.DoesNotExist:
                pass # Should not happen if seeded

        # Update permissions atomically
        with transaction.atomic():
            Role_Permissions.objects.filter(role_id=role).delete()
            for pid in selected_perm_ids:
                perm = Permissions.objects.get(id=pid)
                Role_Permissions.objects.create(role_id=role, permission_id=perm)
        
        messages.success(request, f"Permissions updated successfully for role '{role.role_name}'.")
        log_action(request, 'PERMISSIONS_UPDATED', f"Updated permissions for role: {role.role_name}")
        return redirect('admin_role_permissions')

    # Pre-fetch existing Role_Permissions for easy checking in template
    role_perms = Role_Permissions.objects.select_related('permission_id').all()
    # dict: { role_id: [perm_id1, perm_id2, ...] }
    active_perms = {}
    for rp in role_perms:
        active_perms.setdefault(rp.role_id_id, []).append(rp.permission_id_id)

    # Need ID for critical perms to disable them in UI for Admin
    admin_panel_perm_id = None
    manage_perms_perm_id = None
    try:
        admin_panel_perm_id = Permissions.objects.get(permission_name='can_access_admin_panel').id
        manage_perms_perm_id = Permissions.objects.get(permission_name='can_manage_permissions').id
    except Permissions.DoesNotExist:
        pass

    context = {
        'roles': roles,
        'modules': modules,
        'active_perms': active_perms,
        'critical_admin_perms': [admin_panel_perm_id, manage_perms_perm_id],
    }
    return render(request, 'admin_panel/role_permissions.html', context)
