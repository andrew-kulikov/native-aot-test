"""Benchmark and visualize native-AOT runtime async performance.

Install the plotting dependency once:
    py -m pip install matplotlib

Run from the ConsoleApp directory:
    py benchmark_runtime_async.py
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from statistics import fmean, median, pstdev

import matplotlib.pyplot as plt


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
TIME_PATTERN = re.compile(r"^Time taken:\s*(?P<value>\S+)\s*$", re.MULTILINE)
MEMORY_PATTERNS = {
    "peak_working_set_bytes": re.compile(
        r"^Peak working set:\s*(?P<value>\d+)\s+bytes\s*$", re.MULTILINE
    ),
    "private_memory_bytes": re.compile(
        r"^Private memory:\s*(?P<value>\d+)\s+bytes\s*$", re.MULTILINE
    ),
    "managed_heap_bytes": re.compile(
        r"^Managed heap:\s*(?P<value>\d+)\s+bytes\s*$", re.MULTILINE
    ),
}
EXECUTABLES = {
    "net10.0": SCRIPT_DIRECTORY
    / "bin"
    / "Release"
    / "net10.0"
    / "win-x64"
    / "publish"
    / "ConsoleApp.exe",
    "net11.0": SCRIPT_DIRECTORY
    / "bin"
    / "Release"
    / "net11.0"
    / "win-x64"
    / "publish"
    / "ConsoleApp.exe",
}


def parse_timespan_milliseconds(value: str) -> float:
    """Convert the standard .NET TimeSpan string emitted by Program.cs to ms."""
    days = 0
    if "." in value.split(":")[0]:
        day_part, value = value.split(".", maxsplit=1)
        days = int(day_part)

    hours, minutes, seconds = value.split(":")
    return (
        (((days * 24 + int(hours)) * 60 + int(minutes)) * 60 + float(seconds))
        * 1_000
    )


def run_sample(executable: Path, timeout_seconds: float) -> tuple[float, float, int, int, int]:
    started_at = time.perf_counter()
    result = subprocess.run(
        [str(executable), "4"],
        cwd=SCRIPT_DIRECTORY,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )
    process_milliseconds = (time.perf_counter() - started_at) * 1_000

    if result.returncode != 0:
        raise RuntimeError(
            f"{executable} exited with code {result.returncode}:\n"
            f"{result.stdout}\n{result.stderr}"
        )

    match = TIME_PATTERN.search(result.stdout)
    if match is None:
        raise RuntimeError(
            f"Could not find the 'Time taken' line in output from {executable}:\n"
            f"{result.stdout}\n{result.stderr}"
        )

    memory_values: dict[str, int] = {}
    for column, pattern in MEMORY_PATTERNS.items():
        memory_match = pattern.search(result.stdout)
        if memory_match is None:
            raise RuntimeError(
                f"Could not find '{column}' in output from {executable}. "
                "Re-publish the executable after updating Program.cs."
            )
        memory_values[column] = int(memory_match.group("value"))

    return (
        parse_timespan_milliseconds(match.group("value")),
        process_milliseconds,
        memory_values["peak_working_set_bytes"],
        memory_values["private_memory_bytes"],
        memory_values["managed_heap_bytes"],
    )


def validate_executables() -> None:
    missing = [path for path in EXECUTABLES.values() if not path.is_file()]
    if missing:
        formatted_paths = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(
            "The published executables are missing. Publish both target frameworks first:\n"
            f"{formatted_paths}"
        )


def write_results(rows: list[dict[str, float | int | str]], output_directory: Path) -> None:
    output_file = output_directory / "times.csv"
    with output_file.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "iteration",
                "framework",
                "async_runtime_ms",
                "process_wall_clock_ms",
                "peak_working_set_bytes",
                "private_memory_bytes",
                "managed_heap_bytes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def metric_values(
    rows: list[dict[str, float | int | str]], framework: str, metric: str
) -> list[float]:
    return [
        float(row[metric])
        for row in rows
        if row["framework"] == framework
    ]


def create_line_plot(
    rows: list[dict[str, float | int | str]],
    metric: str,
    scale: float,
    title: str,
    y_label: str,
    output_file: Path,
) -> None:
    figure, axis = plt.subplots(figsize=(12, 6))
    for framework, label, color in (
        ("net10.0", ".NET 10", "#4C78A8"),
        ("net11.0", ".NET 11 (runtime-async=on)", "#F58518"),
    ):
        framework_rows = [row for row in rows if row["framework"] == framework]
        iterations = [int(row["iteration"]) for row in framework_rows]
        values = [float(row[metric]) * scale for row in framework_rows]
        axis.plot(
            iterations,
            values,
            color=color,
            label=label,
            linewidth=1.2,
            marker="o",
            markersize=2.5,
        )

    axis.set_title(title)
    axis.set_xlabel("Paired measurement iteration")
    axis.set_ylabel(y_label)
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_file, dpi=180)
    plt.close(figure)


def create_comparison_histogram(
    rows: list[dict[str, float | int | str]],
    metric: str,
    scale: float,
    title: str,
    x_label: str,
    output_file: Path,
) -> None:
    net10 = [value * scale for value in metric_values(rows, "net10.0", metric)]
    net11 = [value * scale for value in metric_values(rows, "net11.0", metric)]
    bin_count = max(15, min(40, len(net10) // 3))
    lower_bound = min(*net10, *net11)
    upper_bound = max(*net10, *net11)
    if lower_bound == upper_bound:
        bin_edges = [lower_bound - 0.5, upper_bound + 0.5]
    else:
        bin_width = (upper_bound - lower_bound) / bin_count
        bin_edges = [
            lower_bound + index * bin_width for index in range(bin_count + 1)
        ]

    figure, axis = plt.subplots(figsize=(12, 6))
    for values, label, color in (
        (net10, f".NET 10 (n={len(net10)})", "#4C78A8"),
        (net11, f".NET 11 (runtime-async=on, n={len(net11)})", "#F58518"),
    ):
        axis.hist(
            values,
            bins=bin_edges,
            histtype="step",
            linewidth=2,
            color=color,
            label=label,
        )
        axis.axvline(median(values), color=color, linestyle="--", linewidth=1)

    axis.set_title(title)
    axis.set_xlabel(x_label)
    axis.set_ylabel("Number of runs")
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_file, dpi=180)
    plt.close(figure)


def print_summary(rows: list[dict[str, float | int | str]]) -> None:
    print("\nAsync runtime summary (reported by ConsoleApp):")
    for framework in EXECUTABLES:
        values = metric_values(rows, framework, "async_runtime_ms")
        print(
            f"  {framework}: mean={fmean(values):.4f} ms, "
            f"median={median(values):.4f} ms, "
            f"stddev={pstdev(values):.4f} ms, "
            f"min={min(values):.4f} ms, max={max(values):.4f} ms"
        )

    print("\nProcess-memory summary (reported by ConsoleApp):")
    for metric, label in (
        ("peak_working_set_bytes", "peak working set"),
        ("private_memory_bytes", "private memory at exit"),
        ("managed_heap_bytes", "managed heap at exit"),
    ):
        print(f"  {label}:")
        for framework in EXECUTABLES:
            values = [
                value / 1_024**2
                for value in metric_values(rows, framework, metric)
            ]
            print(
                f"    {framework}: mean={fmean(values):.2f} MiB, "
                f"median={median(values):.2f} MiB, "
                f"min={min(values):.2f} MiB, max={max(values):.2f} MiB"
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare native-AOT async runtimes for .NET 10 and .NET 11."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Measured runs per framework (default: 100).",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=10,
        help="Unrecorded runs per framework before measurement (default: 10).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30,
        help="Per-process timeout in seconds (default: 30).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SCRIPT_DIRECTORY / "benchmark-results",
        help="Directory where CSV and PNG files are written.",
    )
    arguments = parser.parse_args()

    if arguments.iterations < 2:
        parser.error("--iterations must be at least 2.")
    if arguments.warmup < 0:
        parser.error("--warmup cannot be negative.")
    if arguments.timeout <= 0:
        parser.error("--timeout must be positive.")

    validate_executables()
    output_directory = arguments.output_dir / datetime.now().strftime("%Y%m%d-%H%M%S")
    output_directory.mkdir(parents=True, exist_ok=False)

    print(f"Warming up each executable {arguments.warmup} times...")
    for framework, executable in EXECUTABLES.items():
        for _ in range(arguments.warmup):
            run_sample(executable, arguments.timeout)

    print(f"Measuring {arguments.iterations} paired iterations...")
    rows: list[dict[str, float | int | str]] = []
    for iteration in range(1, arguments.iterations + 1):
        # Alternate order on each pair so a gradual machine-state change is balanced.
        frameworks = ("net10.0", "net11.0") if iteration % 2 else ("net11.0", "net10.0")
        measurements: dict[str, tuple[float, float, int, int, int]] = {}
        for framework in frameworks:
            measurements[framework] = run_sample(EXECUTABLES[framework], arguments.timeout)

        for framework in EXECUTABLES:
            runtime_ms, process_ms, peak_working_set, private_memory, managed_heap = measurements[
                framework
            ]
            rows.append(
                {
                    "iteration": iteration,
                    "framework": framework,
                    "async_runtime_ms": runtime_ms,
                    "process_wall_clock_ms": process_ms,
                    "peak_working_set_bytes": peak_working_set,
                    "private_memory_bytes": private_memory,
                    "managed_heap_bytes": managed_heap,
                }
            )

        if iteration % 25 == 0 or iteration == arguments.iterations:
            print(f"  Completed {iteration}/{arguments.iterations} paired iterations.")

    write_results(rows, output_directory)
    create_line_plot(
        rows,
        "async_runtime_ms",
        1,
        "Async runtime by measurement iteration",
        "Async runtime (ms)",
        output_directory / "async-runtime-line-plot.png",
    )
    create_comparison_histogram(
        rows,
        "async_runtime_ms",
        1,
        "Async runtime distribution",
        "Async runtime (ms)",
        output_directory / "async-runtime-histogram.png",
    )
    create_line_plot(
        rows,
        "peak_working_set_bytes",
        1 / 1_024**2,
        "Peak process memory by measurement iteration",
        "Peak working set (MiB)",
        output_directory / "peak-working-set-line-plot.png",
    )
    create_comparison_histogram(
        rows,
        "peak_working_set_bytes",
        1 / 1_024**2,
        "Peak process-memory distribution",
        "Peak working set (MiB)",
        output_directory / "peak-working-set-histogram.png",
    )
    print_summary(rows)
    print(f"\nResults written to: {output_directory}")


if __name__ == "__main__":
    main()
