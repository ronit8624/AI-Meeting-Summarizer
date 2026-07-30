import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:flutter_app/models/meeting_model.dart';

class PdfService {
  /// Generates a PDF containing the meeting title and summary.
  static Future<Uint8List> generateSummaryPdf(MeetingModel meeting) async {
    // NotoSans supports special characters (—, ', ", •) that the default
    // PDF font does not, which is why text looked broken before.
    final regularFont = await PdfGoogleFonts.notoSansRegular();
    final boldFont = await PdfGoogleFonts.notoSansBold();

    final doc = pw.Document();

    doc.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(32),
        theme: pw.ThemeData.withFont(
          base: regularFont,
          bold: boldFont,
        ),
        build: (context) => [
          pw.Text(
            meeting.title,
            style: pw.TextStyle(font: boldFont, fontSize: 22),
          ),
          pw.SizedBox(height: 4),
          pw.Divider(),
          pw.SizedBox(height: 12),
          pw.Text(
            'Summary',
            style: pw.TextStyle(font: boldFont, fontSize: 15),
          ),
          pw.SizedBox(height: 8),
          pw.Text(
            _stripMarkdown(meeting.summary),
            style: pw.TextStyle(font: regularFont, fontSize: 12, lineSpacing: 3),
          ),
        ],
      ),
    );

    return doc.save();
  }

  /// Removes markdown syntax (**bold**, #headers, -bullets) for clean PDF text.
  static String _stripMarkdown(String text) {
    return text
        .replaceAllMapped(
          RegExp(r'\*\*(.*?)\*\*'),
          (match) => match.group(1) ?? '',
        )
        .replaceAll(RegExp(r'^#+\s*', multiLine: true), '')
        .replaceAll(RegExp(r'^[-*]\s+', multiLine: true), '•  ')
        .trim();
  }
}