import 'package:flutter/material.dart';
import 'dart:async';
import 'package:provider/provider.dart';
import '../constants/AppColors.dart';
import '../core/StorageService.dart';
import '../view_models/AuthViewModel.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkSession();
  }

  void _checkSession() async {
    // Artificial delay for splash screen visibility
    await Future.delayed(const Duration(seconds: 2));

    final token = await StorageService.getAccessToken();
    if (token != null && mounted) {
      final authViewModel = Provider.of<AuthViewModel>(context, listen: false);
      final success = await authViewModel.fetchUserRole();
      
      if (success && mounted) {
        if (authViewModel.userRole == 'Clinician') {
          Navigator.pushReplacementNamed(context, '/clinician_home');
        } else {
          Navigator.pushReplacementNamed(context, '/patient_home');
        }
        return;
      }
    }
    
    // If no token, or fetching role failed, go to onboarding
    if (mounted) {
      Navigator.pushReplacementNamed(context, '/onboarding');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.lightMint,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Simulating a Logo
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: AppColors.darkTeal,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppColors.darkTeal.withValues(alpha: 0.3),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: const Icon(
                Icons.health_and_safety,
                color: AppColors.white,
                size: 50,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              "RehabTrack",
              style: TextStyle(
                color: AppColors.darkTeal,
                fontSize: 32,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              "Your Journey to Recovery",
              style: TextStyle(
                color: AppColors.darkTeal.withOpacity(0.7),
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.darkTeal),
            ),
          ],
        ),
      ),
    );
  }
}
