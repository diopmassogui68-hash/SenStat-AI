import 'package:flutter/material.dart';
import 'theme/app_theme.dart';
import 'screens/chat_screen.dart';

void main() {
  runApp(const SenStatMobileApp());
}

class SenStatMobileApp extends StatelessWidget {
  const SenStatMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SenStat AI Mobile',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const ChatScreen(),
    );
  }
}
