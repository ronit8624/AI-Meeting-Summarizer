// lib/cards/meeting/transcript_card.dart
// Collapsible transcript viewer

import 'package:flutter/material.dart';
import 'package:flutter_app/theme/app_theme.dart';

class TranscriptCard extends StatefulWidget {
  final String transcript;

  const TranscriptCard({super.key, required this.transcript});

  @override
  State<TranscriptCard> createState() => _TranscriptCardState();
}

class _TranscriptCardState extends State<TranscriptCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with toggle
            GestureDetector(
              onTap: () => setState(() => _expanded = !_expanded),
              child: Row(
                children: [
                  const Text(
                    '📝',
                    style: TextStyle(fontSize: 16),
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'TRANSCRIPT',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textMuted,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    _expanded
                        ? Icons.keyboard_arrow_up
                        : Icons.keyboard_arrow_down,
                    color: AppTheme.textMuted,
                  ),
                ],
              ),
            ),

            // Transcript content
            if (_expanded) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceAlt,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF2A2A3A)),
                ),
                constraints: const BoxConstraints(maxHeight: 300),
                child: SingleChildScrollView(
                  child: Text(
                    widget.transcript,
                    style: const TextStyle(
                      color: AppTheme.textMuted,
                      fontSize: 13,
                      height: 1.7,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}