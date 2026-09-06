import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../constants/AppColors.dart';
import '../components/AppDrawer.dart';
import '../view_models/AuthViewModel.dart';
import '../view_models/PatientDashboardViewModel.dart';

class PatientDashboardScreen extends StatefulWidget {
  const PatientDashboardScreen({super.key});

  @override
  State<PatientDashboardScreen> createState() => _PatientDashboardScreenState();
}

class _PatientDashboardScreenState extends State<PatientDashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<PatientDashboardViewModel>(context, listen: false).fetchDashboardData();
    });
  }

  List<FlSpot> _getPainSpots(List<dynamic> logs) {
    List<FlSpot> spots = [];
    double index = 0;
    // Iterate in reverse so the oldest log is first (left to right)
    for (var log in logs.reversed) {
      final metricValues = log['metric_values'] as List<dynamic>? ?? [];
      for (var mv in metricValues) {
        final metric = mv['metric'] ?? {};
        if (metric['metric_name'] == 'Pain Level') {
          double? val = double.tryParse(mv['value'].toString());
          if (val != null) {
            spots.add(FlSpot(index, val));
            index++;
          }
        }
      }
    }
    return spots;
  }

  @override
  Widget build(BuildContext context) {
    final authViewModel = Provider.of<AuthViewModel>(context);
    final dashboardVM = Provider.of<PatientDashboardViewModel>(context);
    final userName = authViewModel.userName ?? 'Patient';

    final painSpots = _getPainSpots(dashboardVM.progressLogs);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Patient Dashboard', style: TextStyle(color: Colors.white)),
        backgroundColor: AppColors.darkTeal,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      drawer: const AppDrawer(),
      backgroundColor: AppColors.background,
      body: dashboardVM.isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.darkTeal))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome Back, $userName!',
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primaryText),
                  ),
                  const SizedBox(height: 20),
                  
                  // Progress Graph Card
                  if (painSpots.isNotEmpty) ...[
                    Card(
                      elevation: 2,
                      color: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.show_chart, color: AppColors.darkTeal),
                                SizedBox(width: 8),
                                Text('Pain Level Progress', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                              ],
                            ),
                            const Divider(),
                            const SizedBox(height: 16),
                            SizedBox(
                              height: 200,
                              child: LineChart(
                                LineChartData(
                                  gridData: FlGridData(show: false),
                                  titlesData: FlTitlesData(
                                    show: true,
                                    rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                    topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                    bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                    leftTitles: AxisTitles(
                                      sideTitles: SideTitles(
                                        showTitles: true,
                                        reservedSize: 40,
                                        interval: 2,
                                        getTitlesWidget: (value, meta) {
                                          return Text(value.toInt().toString(), style: const TextStyle(color: AppColors.secondaryText, fontSize: 12));
                                        },
                                      ),
                                    ),
                                  ),
                                  borderData: FlBorderData(show: true, border: Border.all(color: Colors.black12)),
                                  minX: 0,
                                  minY: 0,
                                  maxY: 10,
                                  lineBarsData: [
                                    LineChartBarData(
                                      spots: painSpots,
                                      isCurved: true,
                                      color: AppColors.darkTeal,
                                      barWidth: 3,
                                      isStrokeCapRound: true,
                                      dotData: FlDotData(show: true),
                                      belowBarData: BarAreaData(
                                        show: true,
                                        color: AppColors.lightMint.withOpacity(0.3),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Current Rehab Plan Card
                  Card(
                    elevation: 2,
                    color: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.directions_run, color: AppColors.darkTeal),
                              SizedBox(width: 8),
                              Text('Current Plan', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                            ],
                          ),
                          const Divider(),
                          if (dashboardVM.currentPlan != null)
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Cycle: ${dashboardVM.currentPlan!['current_cycle'] ?? 1}', style: const TextStyle(fontWeight: FontWeight.bold)),
                                Text('Status: ${dashboardVM.currentPlan!['status'] ?? 'Active'}', style: const TextStyle(color: AppColors.darkTeal)),
                                const SizedBox(height: 8),
                                Text('Goals: ${dashboardVM.currentPlan!['goals'] ?? 'None'}', style: const TextStyle(color: AppColors.secondaryText)),
                              ],
                            )
                          else
                            const Text('No active rehabilitation plan found.', style: TextStyle(color: Colors.grey)),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Upcoming Appointments Card
                  Card(
                    elevation: 2,
                    color: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.calendar_today, color: AppColors.darkTeal),
                              SizedBox(width: 8),
                              Text('Upcoming Appointments', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                            ],
                          ),
                          const Divider(),
                          if (dashboardVM.upcomingAppointments.isNotEmpty)
                            ListView.builder(
                              shrinkWrap: true,
                              physics: const NeverScrollableScrollPhysics(),
                              itemCount: dashboardVM.upcomingAppointments.length > 3 ? 3 : dashboardVM.upcomingAppointments.length,
                              itemBuilder: (context, index) {
                                final apt = dashboardVM.upcomingAppointments[index];
                                return ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(Icons.schedule, color: AppColors.darkTeal),
                                  title: Text('Date: ${apt['start_time']}'),
                                  subtitle: Text('Status: ${apt['status']}'),
                                );
                              },
                            )
                          else
                            const Text('No appointments scheduled.', style: TextStyle(color: Colors.grey)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
