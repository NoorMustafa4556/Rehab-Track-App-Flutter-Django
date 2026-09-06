import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'constants/AppColors.dart';
import 'views/SplashScreen.dart';
import 'views/OnboardingScreen.dart';
import 'views/LoginScreen.dart';
import 'views/SignUpScreen.dart';
import 'views/HomeScreen.dart';
import 'views/PatientDashboardScreen.dart';
import 'views/ClinicianDashboardScreen.dart';
import 'views/PatientAppointmentsScreen.dart';
import 'views/PatientProgressScreen.dart';
import 'views/ClinicianPatientsScreen.dart';
import 'view_models/AuthViewModel.dart';
import 'view_models/PatientDashboardViewModel.dart';
import 'view_models/ClinicianViewModel.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthViewModel()),
        ChangeNotifierProvider(create: (_) => PatientDashboardViewModel()),
        ChangeNotifierProvider(create: (_) => ClinicianViewModel()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RehabTrack',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: AppColors.darkTeal),
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.background,
        fontFamily: 'Montserrat',
      ),
      initialRoute: '/splash',
      routes: {
        '/splash': (context) => const SplashScreen(),
        '/onboarding': (context) => const OnboardingScreen(),
        '/login': (context) => const LoginScreen(),
        '/signup': (context) => const SignUpScreen(),
        '/home': (context) => const HomeScreen(),
        '/patient_home': (context) => const PatientDashboardScreen(),
        '/clinician_home': (context) => const ClinicianDashboardScreen(),
        '/patient_appointments': (context) => const PatientAppointmentsScreen(),
        '/patient_progress': (context) => const PatientProgressScreen(),
        '/clinician_patients': (context) => const ClinicianPatientsScreen(),
      },
    );
  }
}
