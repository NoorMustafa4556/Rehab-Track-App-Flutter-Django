import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../network/ApiEndpoints.dart';
import '../network/DioClient.dart';
import '../core/StorageService.dart';

class AuthViewModel extends ChangeNotifier {
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  String? _userRole;
  String? get userRole => _userRole;

  String? _userName;
  String? get userName => _userName;

  String? _userEmail;
  String? get userEmail => _userEmail;

  // LOGIN
  Future<bool> login(String username, String password) async {
    _setLoading(true);
    _errorMessage = null;

    try {
      final response = await DioClient.instance.post(
        ApiEndpoints.login,
        data: {
          'username': username,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        final access = data['access'];
        final refresh = data['refresh'];
        
        await StorageService.saveTokens(access: access, refresh: refresh);

        // Fetch User Role
        final roleSuccess = await fetchUserRole();
        _setLoading(false);
        return roleSuccess;
      }
      _setLoading(false);
      return false;
    } on DioException catch (e) {
      if (e.response != null && e.response?.data != null) {
        _errorMessage = e.response?.data['detail'] ?? 'Login failed. Please check your credentials.';
      } else {
        _errorMessage = 'Network error. Please try again.';
      }
      _setLoading(false);
      return false;
    } catch (e) {
      _errorMessage = 'An unexpected error occurred.';
      _setLoading(false);
      return false;
    }
  }

  // SIGNUP
  Future<bool> signup(String username, String email, String password) async {
    _setLoading(true);
    _errorMessage = null;

    try {
      final response = await DioClient.instance.post(
        ApiEndpoints.register,
        data: {
          'username': username,
          'email': email,
          'password': password,
        },
      );

      if (response.statusCode == 201) {
        _setLoading(false);
        return true;
      }
      _setLoading(false);
      return false;
    } on DioException catch (e) {
      if (e.response != null && e.response?.data != null) {
        // Backend typically returns field-specific errors here, e.g. {"username": ["already exists"]}
        _errorMessage = 'Signup failed. Please check your details.';
      } else {
        _errorMessage = 'Network error. Please try again.';
      }
      _setLoading(false);
      return false;
    }
  }

  // FETCH ROLE
  Future<bool> fetchUserRole() async {
    try {
      final response = await DioClient.instance.get(ApiEndpoints.me);
      if (response.statusCode == 200) {
        _userRole = response.data['role']; // e.g., 'Patient' or 'Clinician'
        final profile = response.data['profile'] ?? {};
        final userObj = profile['user'] ?? {};
        _userName = userObj['username'] ?? 'Unknown User';
        _userEmail = userObj['email'] ?? 'No email provided';
        notifyListeners();
        return true;
      }
      return false;
    } on DioException catch (e) {
      _errorMessage = 'Failed to load user profile: ${e.message} - ${e.response?.statusCode}';
      return false;
    } catch (e) {
      _errorMessage = 'Failed to load user profile: $e';
      return false;
    }
  }

  Future<void> logout() async {
    await StorageService.clearTokens();
    _userRole = null;
    notifyListeners();
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
