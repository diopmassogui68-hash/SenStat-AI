class QueryResponse {
  final String answer;
  final List<Map<String, dynamic>> table;
  final ChartConfig? chart;
  final Metadata metadata;

  QueryResponse({
    required this.answer,
    required this.table,
    this.chart,
    required this.metadata,
  });

  factory QueryResponse.fromJson(Map<String, dynamic> json) {
    return QueryResponse(
      answer: json['answer'] as String,
      table: List<Map<String, dynamic>>.from(json['table']),
      chart: json['chart'] != null ? ChartConfig.fromJson(json['chart']) : null,
      metadata: Metadata.fromJson(json['metadata']),
    );
  }
}

class ChartConfig {
  final String type;
  final List<String> labels;
  final List<Dataset> datasets;

  ChartConfig({
    required this.type,
    required this.labels,
    required this.datasets,
  });

  factory ChartConfig.fromJson(Map<String, dynamic> json) {
    return ChartConfig(
      type: json['type'] as String,
      labels: List<String>.from(json['labels']),
      datasets: (json['datasets'] as List)
          .map((data) => Dataset.fromJson(data))
          .toList(),
    );
  }
}

class Dataset {
  final String label;
  final List<double> data;

  Dataset({
    required this.label,
    required this.data,
  });

  factory Dataset.fromJson(Map<String, dynamic> json) {
    return Dataset(
      label: json['label'] as String,
      data: (json['data'] as List).map((e) => (e as num).toDouble()).toList(),
    );
  }
}

class Metadata {
  final bool fictitious;
  final int rowsUsed;

  Metadata({
    required this.fictitious,
    required this.rowsUsed,
  });

  factory Metadata.fromJson(Map<String, dynamic> json) {
    return Metadata(
      fictitious: json['fictitious'] ?? true,
      rowsUsed: json['rows_used'] ?? 0,
    );
  }
}
