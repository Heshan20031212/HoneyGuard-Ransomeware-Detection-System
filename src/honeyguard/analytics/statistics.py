"""
HoneyGuard Statistical Analysis and Charting Utility
Calculates mean, min, max, standard deviation across trials and generates publication-ready charts.
"""

import csv
import math
from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt

from honeyguard.utils.logger import get_logger
from honeyguard.utils.paths import get_benchmark_results_dir, get_project_root

logger = get_logger("HoneyGuard.Statistics")


def calculate_summary_stats(values: List[float]) -> Dict[str, float]:
    """Calculate mean, min, max, and sample standard deviation."""
    if not values:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "std_dev": 0.0, "count": 0}

    count = len(values)
    mean_val = sum(values) / count
    min_val = min(values)
    max_val = max(values)

    if count > 1:
        variance = sum((x - mean_val) ** 2 for x in values) / (count - 1)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 0.0

    return {
        "mean": round(mean_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "std_dev": round(std_dev, 2),
        "count": count
    }


def export_benchmark_csvs(runs: List[Dict[str, Any]], measurements: List[Dict[str, Any]]):
    """Export raw and summary benchmark results to CSV files."""
    results_dir = get_benchmark_results_dir()

    # 1. benchmark_raw.csv
    raw_path = results_dir / "benchmark_raw.csv"
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Run_ID", "Test_Case", "Trial", "Metric_Name", "Metric_Value", "Unit", "Timestamp"])
        for m in measurements:
            writer.writerow([
                m["benchmark_run_id"],
                m.get("test_case", ""),
                m.get("trial", ""),
                m["metric_name"],
                m["metric_value"],
                m["metric_unit"],
                m["sample_timestamp"]
            ])

    # 2. benchmark_summary.csv
    summary_path = results_dir / "benchmark_summary.csv"
    # Aggregate by (test_case, metric_name)
    metric_groups: Dict[tuple, List[float]] = {}
    for m in measurements:
        key = (m.get("test_case", "UNKNOWN"), m["metric_name"])
        metric_groups.setdefault(key, []).append(m["metric_value"])

    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Test_Case", "Metric_Name", "Count", "Mean", "Min", "Max", "Std_Dev"])
        for (tc, mname), vals in sorted(metric_groups.items()):
            stats = calculate_summary_stats(vals)
            writer.writerow([tc, mname, stats["count"], stats["mean"], stats["min"], stats["max"], stats["std_dev"]])

    logger.info(f"Exported benchmark CSVs to {results_dir}")


def generate_benchmark_charts(measurements: List[Dict[str, Any]]):
    """Generate high-resolution PNG charts from genuine benchmark measurements."""
    results_dir = get_benchmark_results_dir()
    evidence_dir = get_project_root() / "docs" / "evidence" / "10_benchmarking"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Dark cybersecurity theme styling for matplotlib
    plt.style.use("dark_background")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.edgecolor": "#30363d",
        "axes.facecolor": "#0d1117",
        "figure.facecolor": "#161b22",
        "grid.color": "#21262d"
    })

    # Group metrics
    groups: Dict[str, Dict[str, List[float]]] = {}
    for m in measurements:
        tc = m.get("test_case", "UNKNOWN")
        metric = m["metric_name"]
        groups.setdefault(metric, {}).setdefault(tc, []).append(m["metric_value"])

    # Chart 1: Detection Time by Scenario
    if "DETECTION_TIME_MS" in groups:
        dt_data = groups["DETECTION_TIME_MS"]
        labels = list(dt_data.keys())
        means = [calculate_summary_stats(dt_data[k])["mean"] for k in labels]
        stds = [calculate_summary_stats(dt_data[k])["std_dev"] for k in labels]

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
        bars = ax.bar(labels, means, yerr=stds, capsize=5, color="#58a6ff", edgecolor="#1f6feb", alpha=0.9)
        ax.set_title("HoneyGuard: Detection Time by Test Scenario (Mean ± Std Dev)", color="#e6edf3", pad=15)
        ax.set_ylabel("Detection Time (milliseconds)", color="#8b949e")
        ax.set_xlabel("Scenario ID", color="#8b949e")
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{h:.1f} ms",
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", color="#58a6ff", fontsize=9, fontweight="bold")
        fig.tight_layout()
        for p in (results_dir / "detection_time_by_scenario.png", evidence_dir / "detection_time_by_scenario.png"):
            fig.savefig(p)
        plt.close(fig)

    # Chart 2: CPU and RAM Usage Comparison
    if "CPU_PERCENT" in groups and "RAM_MB" in groups:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=200)

        # CPU
        cpu_data = groups["CPU_PERCENT"]
        labels = list(cpu_data.keys())
        cpu_means = [calculate_summary_stats(cpu_data[k])["mean"] for k in labels]
        ax1.bar(labels, cpu_means, color="#3fb950", edgecolor="#238636", alpha=0.85)
        ax1.set_title("CPU Utilization Across Scenarios (%)", color="#e6edf3")
        ax1.set_ylabel("Mean CPU Usage (%)", color="#8b949e")
        ax1.grid(axis="y", linestyle="--", alpha=0.4)

        # RAM
        ram_data = groups["RAM_MB"]
        labels = list(ram_data.keys())
        ram_means = [calculate_summary_stats(ram_data[k])["mean"] for k in labels]
        ax2.bar(labels, ram_means, color="#d29922", edgecolor="#9e6a03", alpha=0.85)
        ax2.set_title("Resident Memory Overhead (RAM MB)", color="#e6edf3")
        ax2.set_ylabel("Mean RAM (MB)", color="#8b949e")
        ax2.grid(axis="y", linestyle="--", alpha=0.4)

        fig.tight_layout()
        for p in (results_dir / "resource_usage_overhead.png", evidence_dir / "resource_usage_overhead.png"):
            fig.savefig(p)
        plt.close(fig)

    # Chart 3: Containment Effectiveness
    if "CONTAINMENT_EFFECTIVENESS_PCT" in groups:
        cont_data = groups["CONTAINMENT_EFFECTIVENESS_PCT"]
        labels = list(cont_data.keys())
        means = [calculate_summary_stats(cont_data[k])["mean"] for k in labels]

        fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
        bars = ax.bar(labels, means, color="#f85149", edgecolor="#da3633", alpha=0.85)
        ax.set_title("HoneyGuard: Files Protected / Damage Reduction (%)", color="#e6edf3", pad=15)
        ax.set_ylabel("Damage Reduction (%)", color="#8b949e")
        ax.set_ylim(0, 105)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{h:.1f}%",
                        xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", color="#f85149", fontsize=9, fontweight="bold")
        fig.tight_layout()
        for p in (results_dir / "containment_effectiveness.png", evidence_dir / "containment_effectiveness.png"):
            fig.savefig(p)
        plt.close(fig)

    logger.info(f"Generated benchmark charts in {results_dir} and {evidence_dir}")
