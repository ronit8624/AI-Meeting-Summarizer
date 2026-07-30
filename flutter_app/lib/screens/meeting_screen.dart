// lib/screens/meeting_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_app/notifiers/meeting_notifier.dart';
import 'package:flutter_app/theme/app_theme.dart';
import 'package:flutter_app/widgets/meeting/url_input_widget.dart';
import 'package:flutter_app/widgets/meeting/loading_widget.dart';
import 'package:flutter_app/widgets/meeting/pdf_download_button.dart';
import 'package:flutter_app/cards/meeting/summary_card.dart';
import 'package:flutter_app/cards/meeting/transcript_card.dart';

class MeetingScreen extends StatelessWidget {
  const MeetingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final notifier = context.watch<MeetingNotifier>();

    return Scaffold(
      appBar: AppBar(
        leading: notifier.state == MeetingState.success
            ? IconButton(
                icon: const Icon(Icons.arrow_back_ios),
                onPressed: () => context.read<MeetingNotifier>().reset(),
              )
            : null,
        title: const Text('Meeting Summarizer'),
        actions: [
          if (notifier.state == MeetingState.success)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'New Meeting',
              onPressed: () => context.read<MeetingNotifier>().reset(),
            ),
        ],
      ),
      body: SafeArea(
        child: _buildBody(context, notifier),
      ),
    );
  }

  Widget _buildBody(BuildContext context, MeetingNotifier notifier) {
    switch (notifier.state) {
      case MeetingState.idle:
        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: const UrlInputWidget(),
        );

      case MeetingState.loading:
        return const LoadingWidget();

      case MeetingState.error:
        return Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.error.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.error_outline,
                    color: AppTheme.error,
                    size: 48,
                  ),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Something went wrong',
                  style: TextStyle(
                    color: AppTheme.textPrimary,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  notifier.errorMessage,
                  style: const TextStyle(
                    color: AppTheme.textMuted,
                    fontSize: 14,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: AppTheme.primaryGradient,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ElevatedButton.icon(
                      onPressed: () =>
                          context.read<MeetingNotifier>().reset(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.transparent,
                        shadowColor: Colors.transparent,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      icon: const Icon(Icons.arrow_back,
                          color: Colors.white),
                      label: const Text(
                        'Try Again',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );

      case MeetingState.success:
        final meeting = notifier.meeting!;
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Left half: Summary | Right half: PDF Download
              IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(
                      flex: 1,
                      child: SummaryCard(meeting: meeting),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      flex: 1,
                      child: Center(
                        child: PdfDownloadButton(meeting: meeting),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Transcript
              TranscriptCard(transcript: meeting.transcript),
              const SizedBox(height: 24),
            ],
          ),
        );
    }
  }
}