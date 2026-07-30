// lib/models/meeting_model.dart
// Data model for AI Meeting Summarizer
// Maps exactly to FastAPI SummaryResponse schema

class MeetingModel {
  final String meetingId;
  final String title;
  final String transcript;
  final String summary;
  final String actionItems;
  final String keyDecisions;
  final String openQuestions;
  final String message;

  MeetingModel({
    required this.meetingId,
    required this.title,
    required this.transcript,
    required this.summary,
    required this.actionItems,
    required this.keyDecisions,
    required this.openQuestions,
    required this.message,
  });

  // Convert JSON response from FastAPI to MeetingModel
  factory MeetingModel.fromJson(Map<String, dynamic> json) {
    return MeetingModel(
      meetingId:     json['meeting_id']    ?? '',
      title:         json['title']         ?? '',
      transcript:    json['transcript']    ?? '',
      summary:       json['summary']       ?? '',
      actionItems:   json['action_items']  ?? '',
      keyDecisions:  json['key_decisions'] ?? '',
      openQuestions: json['open_questions'] ?? '',
      message:       json['message']       ?? '',
    );
  }
}