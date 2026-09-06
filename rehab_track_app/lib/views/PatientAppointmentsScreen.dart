import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../view_models/PatientDashboardViewModel.dart';

class PatientAppointmentsScreen extends StatelessWidget {
  const PatientAppointmentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final dashboardVM = Provider.of<PatientDashboardViewModel>(context);
    final upcoming = dashboardVM.upcomingAppointments;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Appointments', style: TextStyle(color: Colors.white)),
        backgroundColor: AppColors.darkTeal,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      backgroundColor: AppColors.background,
      body: upcoming.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.calendar_month, size: 80, color: AppColors.secondaryText),
                  SizedBox(height: 16),
                  Text(
                    'No Appointments Scheduled',
                    style: TextStyle(fontSize: 20, color: AppColors.primaryText, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'You have no upcoming appointments.',
                    style: TextStyle(color: AppColors.secondaryText),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: upcoming.length,
              itemBuilder: (context, index) {
                final apt = upcoming[index];
                
                // Extract clinician name safely
                final clinicianObj = apt['clinician'] ?? {};
                final userObj = clinicianObj['user'] ?? {};
                final clinicianName = userObj['username'] ?? 'Unknown Clinician';
                
                return Card(
                  elevation: 2,
                  color: Colors.white,
                  margin: const EdgeInsets.only(bottom: 12.0),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16.0),
                    leading: const CircleAvatar(
                      backgroundColor: AppColors.lightMint,
                      child: Icon(Icons.calendar_today, color: AppColors.darkTeal),
                    ),
                    title: Text(
                      'Date: ${apt['start_time']}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'Status: ${apt['status']}\nDoctor: $clinicianName',
                      style: const TextStyle(color: AppColors.secondaryText),
                    ),
                    onTap: () {
                      _showAppointmentDetails(context, apt, clinicianName);
                    },
                  ),
                );
              },
            ),
    );
  }

  void _showAppointmentDetails(BuildContext context, dynamic apt, String clinicianName) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Appointment Details',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.darkTeal),
              ),
              const Divider(),
              const SizedBox(height: 12),
              _buildDetailRow(Icons.person, 'Doctor', clinicianName),
              _buildDetailRow(Icons.access_time, 'Start Time', apt['start_time'] ?? 'N/A'),
              _buildDetailRow(Icons.access_time_filled, 'End Time', apt['end_time'] ?? 'N/A'),
              _buildDetailRow(Icons.category, 'Type', apt['type'] ?? 'N/A'),
              _buildDetailRow(Icons.info_outline, 'Status', apt['status'] ?? 'N/A'),
              if (apt['notes'] != null && apt['notes'].toString().isNotEmpty)
                _buildDetailRow(Icons.note, 'Notes', apt['notes']),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.darkTeal,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Close'),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDetailRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: AppColors.secondaryText),
          const SizedBox(width: 12),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(fontSize: 16, color: AppColors.primaryText),
                children: [
                  TextSpan(text: '$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
                  TextSpan(text: value),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
