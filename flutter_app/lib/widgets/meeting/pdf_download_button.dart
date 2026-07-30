import 'package:flutter/material.dart';
import 'package:printing/printing.dart';
import 'package:flutter_app/theme/app_theme.dart';
import 'package:flutter_app/models/meeting_model.dart';
import 'package:flutter_app/api_services/services/pdf_service.dart';

class PdfDownloadButton extends StatefulWidget {
  final MeetingModel meeting;

  const PdfDownloadButton({super.key, required this.meeting});

  @override
  State<PdfDownloadButton> createState() => _PdfDownloadButtonState();
}

class _PdfDownloadButtonState extends State<PdfDownloadButton> {
  bool _isGenerating = false;

  Future<void> _downloadPdf() async {
    setState(() {
      _isGenerating = true;
    });

    try {
      final bytes = await PdfService.generateSummaryPdf(widget.meeting);
      await Printing.sharePdf(
        bytes: bytes,
        filename: '${widget.meeting.title}_summary.pdf',
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to generate PDF: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isGenerating = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.gradientStart.withOpacity(0.15),
            AppTheme.gradientEnd.withOpacity(0.08),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: AppTheme.gradientStart.withOpacity(0.25),
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Center(
              child: Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.gradientStart.withOpacity(0.4),
                      blurRadius: 20,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.picture_as_pdf_outlined,
                  color: Colors.white,
                  size: 40,
                ),
              ),
            ),
            Column(
              children: [
                const Text(
                  'Export Your Summary',
                  style: TextStyle(
                    color: AppTheme.textPrimary,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 10),
                const Text(
                  'Save this meeting summary as a clean,\nshareable PDF document you can send\nto your team or keep for records.',
                  style: TextStyle(
                    color: AppTheme.textMuted,
                    fontSize: 13,
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
            SizedBox(
              height: 52,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ElevatedButton.icon(
                  onPressed: _isGenerating ? null : _downloadPdf,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  icon: _isGenerating
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(
                          Icons.download_outlined,
                          color: Colors.white,
                          size: 20,
                        ),
                  label: Text(
                    _isGenerating ? 'Generating...' : 'Download PDF',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}