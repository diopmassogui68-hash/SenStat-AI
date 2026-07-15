import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/query_response.dart';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ApiService _apiService = ApiService();
  
  final List<MessageItem> _messages = [];
  bool _isLoading = false;

  void _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(MessageItem(text: text, isUser: true));
      _isLoading = true;
      _controller.clear();
    });

    try {
      final response = await _apiService.postQuestion(text);
      setState(() {
        _messages.add(MessageItem(
          text: response.answer,
          isUser: false,
          chart: response.chart,
          table: response.table,
        ));
      });
    } catch (e) {
      setState(() {
        _messages.add(MessageItem(
          text: "Erreur : ${e.toString().replaceAll('Exception: ', '')}",
          isUser: false,
          isError: true,
        ));
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SenStat AI Mobile'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(20),
          child: Container(
            color: Colors.amber,
            width: double.infinity,
            child: const Text(
              'Données pédagogiques fictives (2020-2024)',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.black),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                return _buildMessage(_messages[index]);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
            color: Theme.of(context).colorScheme.surface,
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Posez une question...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                FloatingActionButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  mini: true,
                  child: const Icon(Icons.send),
                )
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessage(MessageItem message) {
    return Align(
      alignment: message.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: message.isUser 
              ? Theme.of(context).colorScheme.primary 
              : (message.isError ? Colors.red.shade100 : Theme.of(context).colorScheme.surfaceContainerHighest),
          borderRadius: BorderRadius.circular(16),
        ),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: TextStyle(
                color: message.isUser 
                    ? Theme.of(context).colorScheme.onPrimary 
                    : (message.isError ? Colors.red.shade900 : Theme.of(context).colorScheme.onSurfaceVariant),
              ),
            ),
            if (message.chart != null) ...[
              const SizedBox(height: 16),
              _buildChart(message.chart!),
            ],
            if (message.table != null && message.table!.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildTable(message.table!),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildChart(ChartConfig config) {
    if (config.type == 'line') {
      return SizedBox(
        height: 200,
        child: LineChart(
          LineChartData(
            lineBarsData: config.datasets.map((d) {
              return LineChartBarData(
                spots: d.data.asMap().entries.map((e) {
                  return FlSpot(e.key.toDouble(), e.value);
                }).toList(),
                isCurved: false,
                color: Theme.of(context).colorScheme.primary,
                barWidth: 2,
              );
            }).toList(),
            titlesData: FlTitlesData(
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  getTitlesWidget: (value, meta) {
                    if (value.toInt() >= 0 && value.toInt() < config.labels.length) {
                      return Text(config.labels[value.toInt()], style: const TextStyle(fontSize: 10));
                    }
                    return const Text('');
                  },
                ),
              ),
            ),
          ),
        ),
      );
    } else {
      return SizedBox(
        height: 200,
        child: BarChart(
          BarChartData(
            barGroups: config.datasets.isNotEmpty ? config.datasets[0].data.asMap().entries.map((e) {
              return BarChartGroupData(
                x: e.key,
                barRods: [
                  BarChartRodData(
                    toY: e.value,
                    color: Theme.of(context).colorScheme.primary,
                  )
                ],
              );
            }).toList() : [],
            titlesData: FlTitlesData(
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  getTitlesWidget: (value, meta) {
                    if (value.toInt() >= 0 && value.toInt() < config.labels.length) {
                      return Text(config.labels[value.toInt()], style: const TextStyle(fontSize: 10));
                    }
                    return const Text('');
                  },
                ),
              ),
            ),
          ),
        ),
      );
    }
  }

  Widget _buildTable(List<Map<String, dynamic>> tableData) {
    if (tableData.isEmpty) return const SizedBox.shrink();
    
    final keys = tableData.first.keys.toList();
    
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowHeight: 40,
        dataRowMinHeight: 30,
        dataRowMaxHeight: 40,
        columns: keys.map((k) => DataColumn(label: Text(k.toUpperCase(), style: const TextStyle(fontSize: 12)))).toList(),
        rows: tableData.map((row) {
          return DataRow(
            cells: keys.map((k) => DataCell(Text(row[k].toString(), style: const TextStyle(fontSize: 12)))).toList(),
          );
        }).toList(),
      ),
    );
  }
}

class MessageItem {
  final String text;
  final bool isUser;
  final bool isError;
  final ChartConfig? chart;
  final List<Map<String, dynamic>>? table;

  MessageItem({
    required this.text,
    required this.isUser,
    this.isError = false,
    this.chart,
    this.table,
  });
}
