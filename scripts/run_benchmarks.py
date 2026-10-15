"""
HoneyGuard Standalone Benchmark Runner
Executes the full 5-trial TC01–TC07 evaluation suite, outputs summary statistics,
and generates publication-ready figures.
"""

from honeyguard.analytics.benchmark import BenchmarkSuite


def main():
    print("==================================================================")
    print("  HONEYGUARD COMPREHENSIVE BENCHMARKING RUNNER (TC01–TC07)")
    print("  Trials per scenario: 5 | Real-Time psutil CPU/RAM Sampling")
    print("==================================================================")

    suite = BenchmarkSuite(trials_per_scenario=5)
    results = suite.execute_full_suite()

    print("\n==================================================================")
    print("  BENCHMARK SUITE EXECUTION SUMMARY")
    print("==================================================================")
    print(f"  • Total Runs Executed:       {results['total_runs']}")
    print(f"  • Telemetry Samples Logged:  {results['total_measurements']}")
    print(f"  • Status:                    {results['status']}")
    print("  • Raw CSV:                   data/benchmark_results/benchmark_raw.csv")
    print("  • Summary CSV:               data/benchmark_results/benchmark_summary.csv")
    print("  • Charts Directory:          data/benchmark_results/")
    print("==================================================================")


if __name__ == "__main__":
    main()
