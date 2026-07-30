// lib/widgets/meeting/url_input_widget.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_app/notifiers/meeting_notifier.dart';
import 'package:flutter_app/theme/app_theme.dart';

enum InputMethod { youtubeUrl, pasteText, uploadFile }

class UrlInputWidget extends StatefulWidget {
  const UrlInputWidget({super.key});

  @override
  State<UrlInputWidget> createState() => _UrlInputWidgetState();
}

class _UrlInputWidgetState extends State<UrlInputWidget> {
  InputMethod _selected = InputMethod.youtubeUrl;
  final TextEditingController _urlController  = TextEditingController();
  final TextEditingController _textController = TextEditingController();
  String? _pickedFileName;

  @override
  void dispose() {
    _urlController.dispose();
    _textController.dispose();
    super.dispose();
  }

  void _onSubmit(BuildContext context) {
    final notifier = context.read<MeetingNotifier>();
    switch (_selected) {
      case InputMethod.youtubeUrl:
        final url = _urlController.text.trim();
        if (url.isEmpty) {
          _showSnack(context, 'Please enter a YouTube URL');
          return;
        }
        notifier.summarizeFromUrl(url);
        break;
      case InputMethod.pasteText:
        final text = _textController.text.trim();
        if (text.isEmpty) {
          _showSnack(context, 'Please paste a transcript');
          return;
        }
        notifier.summarizeFromText(text);
        break;
      case InputMethod.uploadFile:
        _showSnack(context, 'Please select a file first');
        break;
    }
  }

  void _showSnack(BuildContext context, String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg)),
    );
  }

  Future<void> _pickFile(BuildContext context) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'm4a'],
    );
    if (result != null && result.files.isNotEmpty) {
      setState(() => _pickedFileName = result.files.first.name);
      if (context.mounted) {
        context.read<MeetingNotifier>().summarizeFromFilePath(
          result.files.first.path!,
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const SizedBox(height: 16),

        // App badge
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: AppTheme.surfaceAlt,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.gradientStart.withOpacity(0.4)),
          ),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('🎙️', style: TextStyle(fontSize: 16)),
              SizedBox(width: 8),
              Text(
                'AI Meeting Summarizer',
                style: TextStyle(
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Hero title
        const Text(
          'Upload. Transcribe. Summarize.',
          style: TextStyle(
            fontSize: 26,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        const Text(
          'Paste a YouTube link, upload a file, or paste a transcript\n— AI handles the rest.',
          style: TextStyle(color: AppTheme.textMuted, fontSize: 13, height: 1.5),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 28),

        // Input Method Tabs
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Input Method',
                  style: TextStyle(
                    color: AppTheme.gradientStart,
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 12),

                // Tab selector
                _buildTabSelector(),
                const SizedBox(height: 20),

                // Input area
                _buildInputArea(context),
                const SizedBox(height: 16),

                // Submit button
                _buildSubmitButton(context),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTabSelector() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceAlt,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.cardBorder),
      ),
      child: Row(
        children: [
          _tab('YouTube URL', Icons.link, InputMethod.youtubeUrl),
          _tab('Paste Text', Icons.description, InputMethod.pasteText),
          _tab('Upload File', Icons.upload_file, InputMethod.uploadFile),
        ],
      ),
    );
  }

  Widget _tab(String label, IconData icon, InputMethod method) {
    final isSelected = _selected == method;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _selected = method),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            gradient: isSelected ? AppTheme.primaryGradient : null,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 14,
                color: isSelected ? Colors.white : AppTheme.textMuted,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isSelected ? Colors.white : AppTheme.textMuted,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInputArea(BuildContext context) {
    switch (_selected) {
      case InputMethod.youtubeUrl:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'YouTube URL',
              style: TextStyle(
                color: AppTheme.gradientStart,
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _urlController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                hintText: 'https://www.youtube.com/watch?v=...',
                prefixIcon: Icon(Icons.link, color: AppTheme.textMuted, size: 18),
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Paste any YouTube video link. AI will download, transcribe, and summarize.',
              style: TextStyle(color: AppTheme.textMuted, fontSize: 11),
            ),
          ],
        );

      case InputMethod.pasteText:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Paste Transcript',
              style: TextStyle(
                color: AppTheme.gradientStart,
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _textController,
              style: const TextStyle(color: AppTheme.textPrimary, fontSize: 13),
              maxLines: 8,
              decoration: const InputDecoration(
                hintText:
                    'Paste meeting transcript here...\n\nSpeaker 1: Welcome everyone...\nSpeaker 2: Thanks for organizing...',
                alignLabelWithHint: true,
              ),
            ),
          ],
        );

      case InputMethod.uploadFile:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Upload Video / Audio',
              style: TextStyle(
                color: AppTheme.gradientStart,
                fontWeight: FontWeight.w700,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () => _pickFile(context),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 32),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceAlt,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _pickedFileName != null
                        ? AppTheme.gradientStart
                        : AppTheme.cardBorder,
                    style: BorderStyle.solid,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      _pickedFileName != null
                          ? Icons.check_circle
                          : Icons.cloud_upload_outlined,
                      color: _pickedFileName != null
                          ? AppTheme.gradientStart
                          : AppTheme.textMuted,
                      size: 36,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _pickedFileName ?? 'Tap to select video or audio file',
                      style: TextStyle(
                        color: _pickedFileName != null
                            ? AppTheme.gradientStart
                            : AppTheme.textMuted,
                        fontSize: 13,
                        fontWeight: _pickedFileName != null
                            ? FontWeight.w600
                            : FontWeight.normal,
                      ),
                    ),
                    if (_pickedFileName == null)
                      const Padding(
                        padding: EdgeInsets.only(top: 4),
                        child: Text(
                          'MP4, AVI, MOV, MKV, MP3, WAV, and more',
                          style: TextStyle(
                            color: AppTheme.textMuted,
                            fontSize: 11,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        );
    }
  }

  Widget _buildSubmitButton(BuildContext context) {
    String label;
    switch (_selected) {
      case InputMethod.youtubeUrl:
        label = 'Transcribe & Summarize';
        break;
      case InputMethod.pasteText:
        label = 'Generate Summary';
        break;
      case InputMethod.uploadFile:
        label = 'Upload & Summarize';
        break;
    }

    return SizedBox(
      width: double.infinity,
      height: 50,
      child: DecoratedBox(
        decoration: BoxDecoration(
          gradient: AppTheme.primaryGradient,
          borderRadius: BorderRadius.circular(12),
        ),
        child: ElevatedButton(
          onPressed: () => _onSubmit(context),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.transparent,
            shadowColor: Colors.transparent,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
          child: Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 15,
            ),
          ),
        ),
      ),
    );
  }
}