"""HoneyGuard Analytics & Benchmarking Package"""
from honeyguard.analytics.metrics import (
    calculate_detection_time_ms,
    calculate_detection_rate,
    calculate_false_positive_rate,
    calculate_containment_effectiveness
)
from honeyguard.analytics.simulator import SafeSimulator
from honeyguard.analytics.statistics import calculate_summary_stats, export_benchmark_csvs, generate_benchmark_charts
from honeyguard.analytics.benchmark import BenchmarkSuite

__all__ = [
    "calculate_detection_time_ms",
    "calculate_detection_rate",
    "calculate_false_positive_rate",
    "calculate_containment_effectiveness",
    "SafeSimulator",
    "calculate_summary_stats",
    "export_benchmark_csvs",
    "generate_benchmark_charts",
    "BenchmarkSuite"
]
