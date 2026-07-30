// lib/widgets/meeting/chat_widget.dart
// RAG Chat interface for meeting transcript

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_app/notifiers/meeting_notifier.dart';
import 'package:flutter_app/theme/app_theme.dart';

class ChatWidget extends StatefulWidget {
  const ChatWidget({super.key});

  @override
  State<ChatWidget> createState() => _ChatWidgetState();
}

class _ChatWidgetState extends State<ChatWidget> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage(BuildContext context) {
    final question = _controller.text.trim();
    if (question.isEmpty) return;
    _controller.clear();
    context.read<MeetingNotifier>().askQuestion(question);
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final notifier = context.watch<MeetingNotifier>();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            const Row(
              children: [
                Text('💬', style: TextStyle(fontSize: 16)),
                SizedBox(width: 8),
                Text(
                  'CHAT WITH MEETING',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textMuted,
                    letterSpacing: 1.2,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Chat History
            if (notifier.chatHistory.isEmpty)
              Container(
                padding: const EdgeInsets.all(24),
                alignment: Alignment.center,
                child: const Text(
                  'Ask anything about your meeting...',
                  style: TextStyle(
                    color: AppTheme.textMuted,
                    fontSize: 13,
                  ),
                ),
              )
            else
              SizedBox(
                height: 300,
                child: ListView.builder(
                  controller: _scrollController,
                  itemCount: notifier.chatHistory.length,
                  itemBuilder: (context, index) {
                    final msg = notifier.chatHistory[index];
                    final isUser = msg['role'] == 'user';
                    return _chatBubble(
                      content: msg['content'] ?? '',
                      isUser: isUser,
                    );
                  },
                ),
              ),

            // Loading indicator
            if (notifier.chatLoading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: AppTheme.accent,
                      ),
                    ),
                    SizedBox(width: 8),
                    Text(
                      'Thinking...',
                      style: TextStyle(
                        color: AppTheme.textMuted,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 12),

            // Input Row
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    style: const TextStyle(color: AppTheme.textPrimary),
                    decoration: const InputDecoration(
                      hintText: 'Who was assigned the budget review?',
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(context),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: notifier.chatLoading
                      ? null
                      : () => _sendMessage(context),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                    minimumSize: const Size(50, 50),
                  ),
                  child: const Icon(Icons.send),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _chatBubble({required String content, required bool isUser}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            const CircleAvatar(
              radius: 14,
              backgroundColor: AppTheme.accent,
              child: Text('🤖', style: TextStyle(fontSize: 12)),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 14,
                vertical: 10,
              ),
              decoration: BoxDecoration(
                color: isUser
                    ? AppTheme.primary.withOpacity(0.2)
                    : AppTheme.surfaceAlt,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isUser
                      ? AppTheme.primary.withOpacity(0.3)
                      : const Color(0xFF2A2A3A),
                ),
              ),
              child: Text(
                content,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 14,
                  height: 1.5,
                ),
              ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            const CircleAvatar(
              radius: 14,
              backgroundColor: AppTheme.primary,
              child: Text('You', style: TextStyle(fontSize: 9, color: Colors.white)),
            ),
          ],
        ],
      ),
    );
  }
}