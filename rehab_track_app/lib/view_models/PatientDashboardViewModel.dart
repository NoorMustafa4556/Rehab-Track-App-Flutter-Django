import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../network/ApiEndpoints.dart';
import '../network/DioClient.dart';

class PatientDashboardViewModel extends ChangeNotifier {
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  Map<String, dynamic>? _currentPlan;
  Map<String, dynamic>? get currentPlan => _currentPlan;

  List<dynamic> _progressLogs = [];
  List<dynamic> get progressLogs => _progressLogs;

  List<dynamic> _upcomingAppointments = [];
  List<dynamic> get upcomingAppointments => _upcomingAppointments;

  List<dynamic> _pastAppointments = [];
  List<dynamic> get pastAppointments => _pastAppointments;

  Future<void> fetchDashboardData() async {
    _setLoading(true);
    _errorMessage = null;

    try {
      // Fetch all three endpoints concurrently
      await Future.wait([
        _fetchCurrentPlan(),
        _fetchAppointments(),
        _fetchProgressLogs(),
      ]);
    } catch (e) {
      _errorMessage = 'Failed to load some dashboard data.';
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _fetchCurrentPlan() async {
    try {
      final response = await DioClient.instance.get(ApiEndpoints.patientPlan);
      if (response.statusCode == 200) {
        _currentPlan = response.data;
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        _currentPlan = null; // No active plan
      } else {
        rethrow;
      }
    }
  }

  Future<void> _fetchAppointments() async {
    try {
      final response = await DioClient.instance.get(ApiEndpoints.patientAppointments);
      if (response.statusCode == 200) {
        _upcomingAppointments = response.data['upcoming'] ?? [];
        _pastAppointments = response.data['past'] ?? [];
      }
    } on DioException {
      // Ignore individually, will be caught by fetchDashboardData if critical
      _upcomingAppointments = [];
      _pastAppointments = [];
    }
  }

  Future<void> _fetchProgressLogs() async {
    try {
      final response = await DioClient.instance.get(ApiEndpoints.patientProgress);
      if (response.statusCode == 200) {
        _progressLogs = response.data ?? [];
      }
    } on DioException {
      _progressLogs = [];
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
