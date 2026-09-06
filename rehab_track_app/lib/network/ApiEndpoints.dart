import '../core/Config.dart';

class ApiEndpoints {
  static const String baseUrl = Config.apiBaseUrl;

  // Auth
  static const String login = '$baseUrl/auth/login/';
  static const String register = '$baseUrl/auth/register/';
  static const String refresh = '$baseUrl/auth/refresh/';
  static const String me = '$baseUrl/auth/me/';

  // Patient
  static const String patientPlan = '$baseUrl/patient/plan/';
  static const String patientProgress = '$baseUrl/patient/progress/';
  static const String patientAppointments = '$baseUrl/patient/appointments/';

  // Clinician
  static const String clinicianPatients = '$baseUrl/clinician/patients/';
  static const String clinicianAvailability = '$baseUrl/clinician/availability/';
  static const String clinicianAppointments = '$baseUrl/clinician/appointments/';
}
