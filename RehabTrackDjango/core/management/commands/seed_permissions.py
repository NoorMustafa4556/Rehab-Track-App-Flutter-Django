from django.core.management.base import BaseCommand
from core.models import Roles, Permissions, Role_Permissions


PERMISSIONS_SEED = [
    # (permission_name, module, description)
    ('can_access_admin_panel',   'Admin Panel', 'Access the web-based Admin Panel UI'),
    ('can_view_patients',        'Patients',    'View patient records'),
    ('can_edit_patients',        'Patients',    'Edit patient profile data'),
    ('can_delete_patients',      'Patients',    'Soft-delete patient records'),
    ('can_view_clinicians',      'Clinicians',  'View clinician profiles'),
    ('can_edit_clinicians',      'Clinicians',  'Edit clinician availability and profile'),
    ('can_view_appointments',    'Appointments','View appointment schedules'),
    ('can_create_appointments',  'Appointments','Create or schedule new appointments'),
    ('can_view_resources',       'Resources',   'View physical resources (rooms, equipment)'),
    ('can_manage_resources',     'Resources',   'Add or soft-delete resources'),
    ('can_view_reports',         'Reports',     'View 15-week clinical reports'),
    ('can_view_rehab_plans',     'Rehab Plans', 'View rehabilitation plans'),
    ('can_create_rehab_plans',   'Rehab Plans', 'Create new rehabilitation plans and start 15-week cycles'),
    ('can_manage_users',         'Users',       'Create and manage user accounts'),
    ('can_manage_lookups',       'Lookups',     'Add/delete system lookup values (Specializations, etc.)'),
    ('can_manage_permissions',   'Permissions', 'Manage which permissions each role has'),
    ('can_view_activity_logs',   'Activity Logs','View the admin activity audit trail'),
    ('can_log_progress',         'Progress',    'Log patient session progress and metrics'),
    ('can_view_own_progress',    'Progress',    'View own rehabilitation progress and metrics'),
]

# Which permissions each role gets by default (mirrors current hardcoded access)
ROLE_DEFAULTS = {
    'Admin': [
        'can_access_admin_panel', 'can_view_patients', 'can_edit_patients', 'can_delete_patients',
        'can_view_clinicians', 'can_edit_clinicians', 'can_view_appointments', 'can_create_appointments',
        'can_view_resources', 'can_manage_resources', 'can_view_reports', 'can_view_rehab_plans',
        'can_create_rehab_plans', 'can_manage_users', 'can_manage_lookups', 'can_manage_permissions',
        'can_view_activity_logs',
    ],
    'Clinician': [
        'can_view_patients', 'can_view_appointments', 'can_create_appointments',
        'can_view_reports', 'can_view_rehab_plans', 'can_create_rehab_plans', 'can_log_progress',
    ],
    'Patient': [
        'can_view_appointments', 'can_view_rehab_plans', 'can_view_own_progress',
    ],
}


class Command(BaseCommand):
    help = 'Seeds the Permissions and Role_Permissions tables with default data.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding permissions...')

        # Step 1: Create all permission definitions
        perm_objects = {}
        for perm_name, module, description in PERMISSIONS_SEED:
            obj, created = Permissions.objects.get_or_create(
                permission_name=perm_name,
                defaults={'module': module, 'description': description}
            )
            perm_objects[perm_name] = obj
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  [{status}] {perm_name}')

        self.stdout.write('')

        # Step 2: Assign permissions to roles
        for role_name, perm_names in ROLE_DEFAULTS.items():
            try:
                role = Roles.objects.get(role_name=role_name)
            except Roles.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  [SKIP] Role "{role_name}" not found in DB'))
                continue

            assigned = 0
            for perm_name in perm_names:
                perm_obj = perm_objects.get(perm_name)
                if perm_obj:
                    _, created = Role_Permissions.objects.get_or_create(
                        role_id=role,
                        permission_id=perm_obj
                    )
                    if created:
                        assigned += 1

            self.stdout.write(f'  [{role_name}] {assigned} new permissions assigned')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Done! Permission seeding complete.'))
        self.stdout.write(f'  Total permissions: {Permissions.objects.count()}')
        self.stdout.write(f'  Total role-permission links: {Role_Permissions.objects.count()}')
