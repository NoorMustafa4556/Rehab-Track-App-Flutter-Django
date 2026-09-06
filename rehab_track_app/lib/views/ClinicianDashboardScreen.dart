import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../components/AppDrawer.dart';
import '../view_models/AuthViewModel.dart';
import '../view_models/ClinicianViewModel.dart';

class ClinicianDashboardScreen extends StatefulWidget {
  const ClinicianDashboardScreen({super.key});

  @override
  State<ClinicianDashboardScreen> createState() => _ClinicianDashboardScreenState();
}

class _ClinicianDashboardScreenState extends State<ClinicianDashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ClinicianViewModel>(context, listen: false).fetchDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final authViewModel = Provider.of<AuthViewModel>(context);
    final clinicianVM = Provider.of<ClinicianViewModel>(context);
    final userName = authViewModel.userName ?? 'Doctor';

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text("Clinician Dashboard", style: TextStyle(color: Colors.white)),
        backgroundColor: AppColors.darkTeal,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      drawer: const AppDrawer(),
      body: clinicianVM.isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.darkTeal))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome, Dr. $userName!',
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primaryText),
                  ),
                  const SizedBox(height: 20),
                  
                  // Summary Cards
                  Row(
                    children: [
                      Expanded(
                        child: _buildSummaryCard(
                          icon: Icons.people,
                          title: 'My Patients',
                          count: clinicianVM.patients.length.toString(),
                          color: AppColors.darkTeal,
                          onTap: () => Navigator.pushNamed(context, '/clinician_patients'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: _buildSummaryCard(
                          icon: Icons.calendar_today,
                          title: 'Appointments',
                          count: clinicianVM.appointments.length.toString(),
                          color: AppColors.lightMint,
                          textColor: AppColors.darkTeal,
                          onTap: () {},
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  const Text('Upcoming Appointments', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.darkTeal)),
                  const Divider(),
                  
                  if (clinicianVM.appointments.isEmpty)
                    const Padding(
                      padding: EdgeInsets.all(16.0),
                      child: Text('No appointments scheduled today.', style: TextStyle(color: AppColors.secondaryText)),
                    )
                  else
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: clinicianVM.appointments.length,
                      itemBuilder: (context, index) {
                        final apt = clinicianVM.appointments[index];
                        final patientObj = apt['patient'] ?? {};
                        final userObj = patientObj['user'] ?? {};
                        final patientName = userObj['username'] ?? 'Unknown Patient';
                        
                        return Card(
                          elevation: 1,
                          margin: const EdgeInsets.only(bottom: 8.0),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          child: ListTile(
                            leading: const Icon(Icons.schedule, color: AppColors.darkTeal),
                            title: Text('Time: ${apt['start_time']}'),
                            subtitle: Text('Patient: $patientName\nStatus: ${apt['status']}'),
                          ),
                        );
                      },
                    ),
                ],
              ),
            ),
    );
  }

  Widget _buildSummaryCard({required IconData icon, required String title, required String count, required Color color, Color textColor = Colors.white, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2)),
          ]
        ),
        child: Column(
          children: [
            Icon(icon, size: 32, color: textColor),
            const SizedBox(height: 8),
            Text(count, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: textColor)),
            const SizedBox(height: 4),
            Text(title, style: TextStyle(fontSize: 14, color: textColor)),
          ],
        ),
      ),
    );
  }
}
