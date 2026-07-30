// lib/cards/meeting/summary_card.dart
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_app/theme/app_theme.dart';
import 'package:flutter_app/models/meeting_model.dart';

class SummaryCard extends StatelessWidget {
  final MeetingModel meeting;

  const SummaryCard({super.key, required this.meeting});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Generated Title Card
        _sectionCard(
          label: 'Generated Title',
          child: Text(
            meeting.title,
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppTheme.gradientStart,
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Summary Card
        _sectionCard(
          label: 'Summary',
          child: MarkdownBody(
            data: meeting.summary,
            styleSheet: MarkdownStyleSheet(
              p: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 14,
                height: 1.6,
              ),
              strong: const TextStyle(
                color: AppTheme.textPrimary,
                fontWeight: FontWeight.bold,
              ),
              listBullet: const TextStyle(
                color: AppTheme.gradientStart,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _sectionCard({required String label, required Widget child}) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 3,
                  height: 14,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  label,
                  style: const TextStyle(
                    color: AppTheme.gradientStart,
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }
}