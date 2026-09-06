from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# 1. Roles Table
class Roles(models.Model):
    role_name = models.CharField(max_length=50, unique=True) # Admin, Clinician, Patient, Receptionist
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.role_name

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(username, email, password, **extra_fields)

# 2. Users Table
class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role_id = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Required by PermissionsMixin if we want admin access
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_permission(self, perm_name):
        """Check if this user's role has a given permission.
        Uses instance-level caching (_perm_cache) which is naturally
        request-scoped since Django creates a fresh Users instance
        from the session on every request.
        Falls back gracefully to role-name check if DB is empty.
        """
        if not hasattr(self, '_perm_cache'):
            try:
                from core.models import Role_Permissions
                self._perm_cache = set(
                    Role_Permissions.objects
                    .filter(role_id=self.role_id)
                    .values_list('permission_id__permission_name', flat=True)
                )
            except Exception:
                self._perm_cache = set()
        return perm_name in self._perm_cache

# 3. Specializations Table
class Specializations(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# 4. Resource_Types Table
class Resource_Types(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# 5. Patients Table
class Patients(models.Model):
    user_id = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='patient_profile')
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Patient: {self.user_id.username}"

# 6. Clinicians Table
class Clinicians(models.Model):
    user_id = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='clinician_profile')
    specialization_id = models.ForeignKey(Specializations, on_delete=models.SET_NULL, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Clinician: {self.user_id.username}"

# 7. Clinician_Availability Table
class Clinician_Availability(models.Model):
    clinician_id = models.ForeignKey(Clinicians, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_leave = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.clinician_id} on {self.date}"

# 8. Resources Table
class Resources(models.Model):
    name = models.CharField(max_length=100)
    type_id = models.ForeignKey(Resource_Types, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

# 9. Rehabilitation Plans Table
class Rehabilitation_Plans(models.Model):
    patient_id = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name='rehab_plans')
    clinician_id = models.ForeignKey(Clinicians, on_delete=models.SET_NULL, null=True, related_name='assigned_plans')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    current_cycle = models.IntegerField(default=1)
    goals = models.TextField()
    status = models.CharField(max_length=50, default='Active') # Active / Completed / Paused

    def __str__(self):
        return f"Plan for {self.patient_id} - Cycle {self.current_cycle}"

# 10. Assessment_Metrics Table
class Assessment_Metrics(models.Model):
    metric_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.metric_name} ({self.unit})"

# 11. Progress Logs Table
class Progress_Logs(models.Model):
    plan_id = models.ForeignKey(Rehabilitation_Plans, on_delete=models.CASCADE, related_name='progress_logs')
    log_date = models.DateField()
    treatment_given = models.TextField()
    clinician_notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Log on {self.log_date} for Plan {self.plan_id_id}"

# 12. Progress_Metric_Values Table
class Progress_Metric_Values(models.Model):
    log_id = models.ForeignKey(Progress_Logs, on_delete=models.CASCADE, related_name='metric_values')
    metric_id = models.ForeignKey(Assessment_Metrics, on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        return f"{self.metric_id.metric_name}: {self.value}"

# 13. Appointments Table
class Appointments(models.Model):
    patient_id = models.ForeignKey(Patients, on_delete=models.CASCADE, related_name='appointments')
    clinician_id = models.ForeignKey(Clinicians, on_delete=models.CASCADE, related_name='appointments')
    resource_id = models.ForeignKey(Resources, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50, default='Booked') # Booked / Cancelled / Rescheduled / Completed
    is_auto_scheduled = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment on {self.start_time}"

# 14. AI Analytics Table
class AI_Analytics(models.Model):
    plan_id = models.ForeignKey(Rehabilitation_Plans, on_delete=models.CASCADE, related_name='ai_predictions')
    predicted_recovery_weeks = models.IntegerField(blank=True, null=True)
    plateau_risk_score = models.FloatField(blank=True, null=True)
    intervention_advice = models.TextField(blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for Plan {self.plan_id_id} at {self.generated_at}"

# 15. Clinical Reports Table
class Clinical_Reports(models.Model):
    plan_id = models.ForeignKey(Rehabilitation_Plans, on_delete=models.CASCADE, related_name='reports')
    cycle_number = models.IntegerField()
    summary = models.TextField()
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report Cycle {self.cycle_number} for Plan {self.plan_id_id}"

# 16. Notifications Table
class Notifications(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user_id.username} - {self.title}"

# 17. Activity Logs Table
class Activity_Logs(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity: {self.action} by {self.user_id} at {self.timestamp}"

# 18. Permissions Table (Dynamic Permission Definitions)
class Permissions(models.Model):
    permission_name = models.CharField(max_length=100, unique=True)
    module = models.CharField(max_length=50)  # e.g. "Patients", "Resources"
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.module}: {self.permission_name}"

    class Meta:
        ordering = ['module', 'permission_name']

# 19. Role_Permissions Table (Join Table — Which Role Has Which Permission)
class Role_Permissions(models.Model):
    role_id = models.ForeignKey(Roles, on_delete=models.CASCADE, related_name='role_permissions')
    permission_id = models.ForeignKey(Permissions, on_delete=models.CASCADE, related_name='role_permissions')

    class Meta:
        unique_together = ('role_id', 'permission_id')

    def __str__(self):
        return f"{self.role_id.role_name} → {self.permission_id.permission_name}"
