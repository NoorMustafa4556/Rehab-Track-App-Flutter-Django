import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../view_models/AuthViewModel.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    final authViewModel = Provider.of<AuthViewModel>(context);
    final userRole = authViewModel.userRole ?? 'Unknown Role';
    final userName = authViewModel.userName ?? 'User';
    final userEmail = authViewModel.userEmail ?? 'user@example.com';

    return Drawer(
      child: Column(
        children: [
          UserAccountsDrawerHeader(
            decoration: const BoxDecoration(color: AppColors.darkTeal),
            accountName: Text('$userName ($userRole)'),
            accountEmail: Text(userEmail),
            currentAccountPicture: const CircleAvatar(
              backgroundColor: Colors.white,
              child: Icon(Icons.person, size: 40, color: AppColors.darkTeal),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('Dashboard'),
            onTap: () {
              Navigator.pop(context);
            },
          ),
          ListTile(
            leading: const Icon(Icons.calendar_month),
            title: const Text('Appointments'),
            onTap: () {
              Navigator.pop(context);
              Navigator.pushNamed(context, '/patient_appointments');
            },
          ),
          if (userRole == 'Patient')
            ListTile(
              leading: const Icon(Icons.monitor_heart),
              title: const Text('My Progress'),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/patient_progress');
              },
            ),
          if (userRole == 'Clinician')
            ListTile(
              leading: const Icon(Icons.people),
              title: const Text('My Patients'),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/clinician_patients');
              },
            ),
          const Spacer(),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.redAccent),
            title: const Text('Logout', style: TextStyle(color: Colors.redAccent)),
            onTap: () async {
              Navigator.pop(context); // Close drawer
              await authViewModel.logout();
              if (context.mounted) {
                Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
              }
            },
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}
