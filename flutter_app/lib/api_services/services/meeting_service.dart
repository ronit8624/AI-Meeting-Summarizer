// lib/api_services/services/meeting_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_app/models/meeting_model.dart';

class MeetingApiService {
  static const String _baseUrl = 'http://127.0.0.1:8000';

  final Dio _dio = Dio(BaseOptions(
    baseUrl: _baseUrl,
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(minutes: 10),
    headers: {'Content-Type': 'application/json'},
  ));

  // ── YouTube URL ───────────────────────────────────────────────
  Future<MeetingModel> summarizeFromUrl(String youtubeUrl) async {
    try {
      final response = await _dio.post(
        '/api/v1/meeting/summarize',
        data: jsonEncode({'youtube_url': youtubeUrl}),
      );
      return MeetingModel.fromJson(response.data);
    } on DioException catch (e) {
      throw Exception(
        e.response?.data['detail'] ?? 'Failed to connect to server.',
      );
    }
  }

  // ── Paste Text ────────────────────────────────────────────────
  Future<MeetingModel> summarizeFromText(String text) async {
    try {
      final response = await _dio.post(
        '/api/v1/meeting/summarize',
        data: jsonEncode({'transcript_text': text}),
      );
      return MeetingModel.fromJson(response.data);
    } on DioException catch (e) {
      throw Exception(
        e.response?.data['detail'] ?? 'Failed to connect to server.',
      );
    }
  }

  // ── File Upload ───────────────────────────────────────────────
  Future<MeetingModel> summarizeFromFile(String filePath) async {
    try {
      // Step 1: Upload file
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          filename: filePath.split('/').last,
        ),
      });

      final uploadResponse = await _dio.post(
        '/api/v1/meeting/upload',
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
          receiveTimeout: const Duration(minutes: 5),
        ),
      );

      final meetingId = uploadResponse.data['meeting_id'];

      // Step 2: Summarize
      final summarizeResponse = await _dio.post(
        '/api/v1/meeting/summarize',
        data: jsonEncode({'meeting_id': meetingId}),
      );

      return MeetingModel.fromJson(summarizeResponse.data);
    } on DioException catch (e) {
      throw Exception(
        e.response?.data['detail'] ?? 'Failed to upload file.',
      );
    }
  }

  // ── Chat ──────────────────────────────────────────────────────
  Future<String> chat(String meetingId, String question) async {
    try {
      final response = await _dio.post(
        '/api/v1/meeting/chat',
        data: jsonEncode({
          'meeting_id': meetingId,
          'question': question,
        }),
      );
      return response.data['answer'] ?? '';
    } on DioException catch (e) {
      throw Exception(
        e.response?.data['detail'] ?? 'Failed to get answer.',
      );
    }
  }
}