// lib/notifiers/meeting_notifier.dart
import 'package:flutter/foundation.dart';
import 'package:flutter_app/models/meeting_model.dart';
import 'package:flutter_app/api_services/services/meeting_service.dart';

enum MeetingState { idle, loading, success, error }

class MeetingNotifier extends ChangeNotifier {
  final MeetingApiService _apiService = MeetingApiService();

  MeetingState _state = MeetingState.idle;
  MeetingModel? _meeting;
  String _errorMessage = '';
  List<Map<String, String>> _chatHistory = [];
  bool _chatLoading = false;

  MeetingState get state => _state;
  MeetingModel? get meeting => _meeting;
  String get errorMessage => _errorMessage;
  List<Map<String, String>> get chatHistory => _chatHistory;
  bool get chatLoading => _chatLoading;

  // ── YouTube URL ───────────────────────────────────────────────
  Future<void> summarizeFromUrl(String youtubeUrl) async {
    _startLoading();
    try {
      _meeting = await _apiService.summarizeFromUrl(youtubeUrl);
      _state = MeetingState.success;
    } catch (e) {
      _setError(e.toString());
    }
    notifyListeners();
  }

  // ── Paste Text ────────────────────────────────────────────────
  Future<void> summarizeFromText(String text) async {
    _startLoading();
    try {
      _meeting = await _apiService.summarizeFromText(text);
      _state = MeetingState.success;
    } catch (e) {
      _setError(e.toString());
    }
    notifyListeners();
  }

  // ── File Upload ───────────────────────────────────────────────
  Future<void> summarizeFromFilePath(String filePath) async {
    _startLoading();
    try {
      _meeting = await _apiService.summarizeFromFile(filePath);
      _state = MeetingState.success;
    } catch (e) {
      _setError(e.toString());
    }
    notifyListeners();
  }

  // ── Chat ──────────────────────────────────────────────────────
  Future<void> askQuestion(String question) async {
    if (_meeting == null) return;
    _chatHistory.add({'role': 'user', 'content': question});
    _chatLoading = true;
    notifyListeners();

    try {
      final answer = await _apiService.chat(_meeting!.meetingId, question);
      _chatHistory.add({'role': 'assistant', 'content': answer});
    } catch (e) {
      _chatHistory.add({
        'role': 'assistant',
        'content': 'Error: ${e.toString().replaceAll('Exception: ', '')}',
      });
    }
    _chatLoading = false;
    notifyListeners();
  }

  // ── Reset ─────────────────────────────────────────────────────
  void reset() {
    _state = MeetingState.idle;
    _meeting = null;
    _errorMessage = '';
    _chatHistory = [];
    _chatLoading = false;
    notifyListeners();
  }

  // ── Helpers ───────────────────────────────────────────────────
  void _startLoading() {
    _state = MeetingState.loading;
    _meeting = null;
    _errorMessage = '';
    _chatHistory = [];
    notifyListeners();
  }

  void _setError(String e) {
    _state = MeetingState.error;
    _errorMessage = e.replaceAll('Exception: ', '');
  }
}