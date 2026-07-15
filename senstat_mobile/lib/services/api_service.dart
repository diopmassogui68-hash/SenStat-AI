import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/query_response.dart';

class ApiService {
  // En dev local, on pointe sur le serveur Django qui tourne sur le port 8000
  static const String baseUrl = 'http://127.0.0.1:8000/api';

  Future<QueryResponse> postQuestion(String question) async {
    final response = await http.post(
      Uri.parse('$baseUrl/question/'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'question': question}),
    );

    if (response.statusCode == 200) {
      final jsonResponse = jsonDecode(response.body);
      return QueryResponse.fromJson(jsonResponse);
    } else {
      // Gestion d'erreur basique
      final Map<String, dynamic> errorBody = jsonDecode(response.body);
      final errorMsg = errorBody.containsKey('question')
          ? errorBody['question'][0]
          : 'Erreur réseau (code ${response.statusCode})';
      throw Exception(errorMsg);
    }
  }
}
