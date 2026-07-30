// lib/widgets/meeting/loading_widget.dart
// Loading indicator shown while AI pipeline is running

import 'package:flutter/material.dart';
import 'package:flutter_app/theme/app_theme.dart';

class LoadingWidget extends StatelessWidget {
  const LoadingWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Purple circular progress
          const CircularProgressIndicator(
            color: AppTheme.primary,
            strokeWidth: 3,
          ),
          const SizedBox(height: 24),

          const Text(
            '⚙️ Pipeline Running...',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 12),

          const Text(
            'Transcribing · Diarizing · Summarizing',
            style: TextStyle(
              fontSize: 13,
              color: AppTheme.textMuted,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 24),

          // Status badges
          Wrap(
            spacing: 8,
            children: [
              _badge('faster-whisper', AppTheme.primary),
              _badge('Pyannote', AppTheme.accent),
              _badge('Mistral', AppTheme.success),
            ],
          ),
        ],
      ),
    );
  }

  Widget _badge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}