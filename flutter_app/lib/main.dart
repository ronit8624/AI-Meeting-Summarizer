// lib/main.dart
// Entry point for AI Meeting Summarizer Flutter app

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_app/notifiers/meeting_notifier.dart';
import 'package:flutter_app/routes/app_router.dart';
import 'package:flutter_app/theme/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MeetingNotifier(),
      child: MaterialApp(
        title: 'AI Meeting Summarizer',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        onGenerateRoute: AppRouter.generateRoute,
        initialRoute: AppRouter.meeting,
      ),
    );
  }
}