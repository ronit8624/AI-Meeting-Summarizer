// lib/routes/app_router.dart
// Navigation and routing configuration

import 'package:flutter/material.dart';
import 'package:flutter_app/screens/meeting_screen.dart';

class AppRouter {
  static const String meeting = '/';

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case meeting:
        return MaterialPageRoute(
          builder: (_) => const MeetingScreen(),
        );
      default:
        return MaterialPageRoute(
          builder: (_) => const MeetingScreen(),
        );
    }
  }
}