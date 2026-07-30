// lib/providers/meeting_provider.dart
// Links MeetingNotifier to the widget tree via Provider

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_app/notifiers/meeting_notifier.dart';

// Call this in main.dart to inject MeetingNotifier into widget tree
class MeetingProvider extends StatelessWidget {
  final Widget child;

  const MeetingProvider({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MeetingNotifier(),
      child: child,
    );
  }
}

// Helper extension for easy access anywhere in widget tree
extension MeetingProviderExtension on BuildContext {
  MeetingNotifier get meetingNotifier => read<MeetingNotifier>();
  MeetingNotifier get watchMeeting => watch<MeetingNotifier>();
}