from django.contrib import admin
from .models import Roles, Users, Patients, Clinicians, Specializations, Appointments, Rehabilitation_Plans, Progress_Logs

# Customizing User Admin to show important fields
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role_id', 'is_active', 'is_staff')
    list_filter = ('role_id', 'is_active', 'is_staff')
    search_fields = ('username', 'email')

class CliniciansAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'specialization_id', 'is_available')
    list_filter = ('is_available', 'specialization_id')

class PatientsAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'gender', 'dob')

admin.site.register(Roles)
admin.site.register(Users, UsersAdmin)
admin.site.register(Patients, PatientsAdmin)
admin.site.register(Clinicians, CliniciansAdmin)
admin.site.register(Specializations)
admin.site.register(Appointments)
admin.site.register(Rehabilitation_Plans)
admin.site.register(Progress_Logs)
