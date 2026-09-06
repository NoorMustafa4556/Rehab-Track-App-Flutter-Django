import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../view_models/PatientDashboardViewModel.dart';

class PatientProgressScreen extends StatelessWidget {
  const PatientProgressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final dashboardVM = Provider.of<PatientDashboardViewModel>(context);
    final logs = dashboardVM.progressLogs;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Progress', style: TextStyle(color: Colors.white)),
        backgroundColor: AppColors.darkTeal,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      backgroundColor: AppColors.background,
      body: logs.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.monitor_heart, size: 80, color: AppColors.secondaryText),
                  SizedBox(height: 16),
                  Text(
                    'No Progress Logs Yet',
                    style: TextStyle(fontSize: 20, color: AppColors.primaryText, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Your clinician hasn\'t added any progress logs yet.',
                    style: TextStyle(color: AppColors.secondaryText),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: logs.length,
              itemBuilder: (context, index) {
                final log = logs[index];
                
                // Parse pain level safely from metric_values
                String painLevel = 'N/A';
                final metricValues = log['metric_values'] as List<dynamic>? ?? [];
                for (var mv in metricValues) {
                  final metric = mv['metric'] ?? {};
                  if (metric['metric_name'] == 'Pain Level') {
                    painLevel = mv['value'].toString();
                    break;
                  }
                }
                
                final clinicianNotes = log['clinician_notes'] ?? 'None';
                final doctorName = log['created_by_name'] ?? 'Unknown';

                return Card(
                  elevation: 2,
                  color: Colors.white,
                  margin: const EdgeInsets.only(bottom: 12.0),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16.0),
                    leading: const CircleAvatar(
                      backgroundColor: AppColors.lightMint,
                      child: Icon(Icons.monitor_heart, color: AppColors.darkTeal),
                    ),
                    title: Text(
                      'Date: ${log['log_date']}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'Pain Level: $painLevel\nBy: Dr. $doctorName',
                      style: const TextStyle(color: AppColors.secondaryText),
                    ),
                    onTap: () {
                      _showProgressDetails(context, log, painLevel, clinicianNotes, doctorName, metricValues);
                    },
                  ),
                );
              },
            ),
    );
  }

  void _showProgressDetails(BuildContext context, dynamic log, String painLevel, String clinicianNotes, String doctorName, List<dynamic> metricValues) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Progress Log Details',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.darkTeal),
                ),
                const Divider(),
                const SizedBox(height: 12),
                _buildDetailRow(Icons.calendar_today, 'Date', log['log_date'] ?? 'N/A'),
                _buildDetailRow(Icons.person, 'Recorded By', 'Dr. $doctorName'),
                _buildDetailRow(Icons.monitor_heart, 'Pain Level', painLevel),
                
                if (log['treatment_given'] != null && log['treatment_given'].toString().isNotEmpty)
                  _buildDetailRow(Icons.medical_services, 'Treatment', log['treatment_given']),
                  
                _buildDetailRow(Icons.note, 'Notes', clinicianNotes),
                
                if (metricValues.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text('All Metrics:', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.darkTeal)),
                  const SizedBox(height: 8),
                  ...metricValues.map((mv) {
                    final mName = mv['metric']?['metric_name'] ?? 'Unknown Metric';
                    final mUnit = mv['metric']?['unit'] ?? '';
                    final mVal = mv['value'] ?? 'N/A';
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4.0),
                      child: Text('• $mName: $mVal $mUnit', style: const TextStyle(color: AppColors.secondaryText)),
                    );
                  }),
                ],
                
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
