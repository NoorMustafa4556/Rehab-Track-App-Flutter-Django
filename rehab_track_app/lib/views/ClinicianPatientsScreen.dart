import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../view_models/ClinicianViewModel.dart';
import '../components/AppDrawer.dart';
import '../components/LogProgressBottomSheet.dart';

class ClinicianPatientsScreen extends StatefulWidget {
  const ClinicianPatientsScreen({super.key});

  @override
  State<ClinicianPatientsScreen> createState() => _ClinicianPatientsScreenState();
}

class _ClinicianPatientsScreenState extends State<ClinicianPatientsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ClinicianViewModel>(context, listen: false).fetchDashboardData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final clinicianVM = Provider.of<ClinicianViewModel>(context);
    final plans = clinicianVM.patients;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text("My Patients", style: TextStyle(color: Colors.white)),
        backgroundColor: AppColors.darkTeal,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      drawer: const AppDrawer(),
      body: clinicianVM.isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.darkTeal))
          : plans.isEmpty
              ? const Center(
                  child: Text(
                    "No active or paused patients assigned to you.",
                    style: TextStyle(color: AppColors.secondaryText, fontSize: 16),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16.0),
                  itemCount: plans.length,
                  itemBuilder: (context, index) {
                    final plan = plans[index];
                    final patientObj = plan['patient'] ?? {};
                    final userObj = patientObj['user'] ?? {};
                    final patientName = userObj['username'] ?? 'Unknown Patient';
                    final planStatus = plan['status'] ?? 'Unknown';
                    final patientId = patientObj['id'];

                    return Card(
                      elevation: 2,
                      color: Colors.white,
                      margin: const EdgeInsets.only(bottom: 12.0),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16.0),
                        leading: const CircleAvatar(
                          backgroundColor: AppColors.lightMint,
                          child: Icon(Icons.person, color: AppColors.darkTeal),
                        ),
                        title: Text(
                          patientName,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                        ),
                        subtitle: Text(
                          'Status: $planStatus\nCycle: ${plan['current_cycle'] ?? 1}',
                          style: const TextStyle(color: AppColors.secondaryText),
                        ),
                        trailing: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.darkTeal,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          onPressed: () {
                            // Show Log Progress Bottom Sheet
                            if (patientId != null) {
                              LogProgressBottomSheet.show(context, patientId, patientName);
                            }
                          },
                          child: const Text('Log Progress'),
                        ),
                        onTap: () {
                          // Could navigate to a detailed view if needed
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
