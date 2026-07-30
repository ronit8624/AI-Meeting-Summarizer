// lib/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  // ── Colors ───────────────────────────────────────────────────
  static const Color background  = Color(0xFF0F1923);
  static const Color surface     = Color(0xFF1A2535);
  static const Color surfaceAlt  = Color(0xFF243044);
  static const Color cardBorder  = Color(0xFF2A3F55);
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textMuted   = Color(0xFF8899AA);
  static const Color error       = Color(0xFFEF4444);

  // Legacy aliases
  static const Color primary = gradientStart;
  static const Color accent  = gradientEnd;
  static const Color success = Color(0xFF10B981);

  // Green gradient colors
  static const Color gradientStart = Color(0xFF00C896);
  static const Color gradientEnd   = Color(0xFF00A8E8);

  // Gradient
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [gradientStart, gradientEnd],
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
  );

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: const ColorScheme.dark(
        primary: gradientStart,
        secondary: gradientEnd,
        surface: surface,
        error: error,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        foregroundColor: textPrimary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceAlt,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: cardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: cardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: gradientStart),
        ),
        hintStyle: const TextStyle(color: textMuted),
        labelStyle: const TextStyle(color: textMuted),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: cardBorder),
        ),
      ),
    );
  }
}