import 'package:flutter/material.dart';
import '../network/DioClient.dart';
import '../core/Config.dart';

class ClinicianViewModel extends ChangeNotifier {
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  List<dynamic> _patients = [];
  List<dynamic> get patients => _patients;

  List<dynamic> _appointments = [];
  List<dynamic> get appointments => _appointments;

  // Selected Patient details
  Map<String, dynamic>? _selectedPatientPlan;
  Map<String, dynamic>? get selectedPatientPlan => _selectedPatientPlan;

  List<dynamic> _selectedPatientLogs = [];
  List<dynamic> get selectedPatientLogs => _selectedPatientLogs;

  List<dynamic> _availableMetrics = [];
  List<dynamic> get availableMetrics => _availableMetrics;

  Future<void> fetchDashboardData() async {
    _isLoading = true;
    notifyListeners();

    try {
      final dio = await DioClient.getDio();
      
      // Fetch Patients
      final patientsRes = await dio.get('${Config.apiBaseUrl}/clinician/patients/');
      if (patientsRes.statusCode == 200) {
        _patients = patientsRes.data;
      }

      // Fetch Appointments
      final apptRes = await dio.get('${Config.apiBaseUrl}/clinician/appointments/');
      if (apptRes.statusCode == 200) {
        _appointments = apptRes.data;
      }
    } catch (e) {
      debugPrint("Error fetching clinician dashboard data: $e");
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchPatientDetail(int patientId) async {
    _isLoading = true;
    notifyListeners();

    try {
      final dio = await DioClient.getDio();
      final res = await dio.get('${Config.apiBaseUrl}/clinician/patients/$patientId/');
      
      if (res.statusCode == 200) {
        _selectedPatientPlan = res.data['plan'];
        _selectedPatientLogs = res.data['logs'];
        _availableMetrics = res.data['available_metrics'];
      }
    } catch (e) {
      debugPrint("Error fetching patient detail: $e");
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addProgressLog(int patientId, String treatmentGiven, String notes, Map<String, dynamic> metricsData) async {
    try {
      final dio = await DioClient.getDio();
      final res = await dio.post(
        '${Config.apiBaseUrl}/clinician/patients/$patientId/progress/add/',
        data: {
          'treatment_given': treatmentGiven,
          'clinician_notes': notes,
          'metrics': metricsData,
        },
      );
      
      if (res.statusCode == 201) {
        // Refresh details
        await fetchPatientDetail(patientId);
        return true;
      }
    } catch (e) {
      debugPrint("Error adding progress log: $e");
    }
    return false;
  }
}
