// lib/cards/meeting/action_items_card.dart
// Displays action items, key decisions, open questions

import 'package:flutter/material.dart';
import 'package:flutter_app/theme/app_theme.dart';

class ActionItemsCard extends StatelessWidget {
  final String actionItems;
  final String keyDecisions;
  final String openQuestions;

  const ActionItemsCard({
    super.key,
    required this.actionItems,
    required this.keyDecisions,
    required this.openQuestions,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _insightCard(
          icon: '✅',
          label: 'Action Items',
          content: actionItems,
          color: AppTheme.success,
        ),
        const SizedBox(height: 12),
        _insightCard(
          icon: '🔑',
          label: 'Key Decisions',
          content: keyDecisions,
          color: AppTheme.accent,
        ),
        const SizedBox(height: 12),
        _insightCard(
          icon: '❓',
          label: 'Open Questions',
          content: openQuestions,
          color: AppTheme.primary,
        ),
      ],
    );
  }

  Widget _insightCard({
    required String icon,
    required String label,
    required String content,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Text(icon, style: const TextStyle(fontSize: 16)),
                const SizedBox(width: 8),
                Text(
                  label.toUpperCase(),
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: color,
                    letterSpacing: 1.2,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Content
            Text(
              content,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 14,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }
}