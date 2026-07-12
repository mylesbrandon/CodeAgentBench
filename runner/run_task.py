from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Stores the result of one pytest test suite."""

    name: str
    passed: bool
    return_code: int
    duration_seconds: float
    output: str


def clear_python_cache(task_dir: Path) -> None:
    """
    Remove cached Python bytecode.

    This prevents Python from accidentally using an older cached version
    of starter.py after the runner swaps in a candidate solution.
    """
    cache_dir = task_dir / "__pycache__"
    shutil.rmtree(cache_dir, ignore_errors=True)


def run_test_suite(
    task_dir: Path,
    test_filename: str,
    suite_name: str,
) -> TestResult:
    """
    Run one pytest file inside the task directory.

    Running pytest in a subprocess keeps the runner isolated from errors
    in the candidate solution.
    """
    test_path = task_dir / test_filename

    if not test_path.exists():
        return TestResult(
            name=suite_name,
            passed=False,
            return_code=1,
            duration_seconds=0.0,
            output=f"Missing test file: {test_path}",
        )

    clear_python_cache(task_dir)

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    start_time = time.perf_counter()

    completed_process = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            test_filename,
            "-q",
        ],
        cwd=task_dir,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )

    duration = time.perf_counter() - start_time

    output_parts = [
        completed_process.stdout.strip(),
        completed_process.stderr.strip(),
    ]
    output = "\n".join(part for part in output_parts if part)

    return TestResult(
        name=suite_name,
        passed=completed_process.returncode == 0,
        return_code=completed_process.returncode,
        duration_seconds=duration,
        output=output,
    )


def print_result(result: TestResult, show_full_output: bool) -> None:
    """Print a readable result for one test suite."""
    status = "PASS" if result.passed else "FAIL"

    print(
        f"{result.name}: {status} "
        f"({result.duration_seconds:.2f} seconds)"
    )

    if show_full_output or not result.passed:
        print()
        print(result.output or "No pytest output.")
        print()


def resolve_solution_path(
    solution_argument: str | None,
    task_dir: Path,
) -> Path | None:
    """
    Resolve the optional candidate solution path.

    This supports either:
    - a path relative to the project root/current directory
    - a filename inside the task directory
    """
    if solution_argument is None:
        return None

    supplied_path = Path(solution_argument).expanduser()

    if supplied_path.exists():
        return supplied_path.resolve()

    task_relative_path = task_dir / supplied_path

    if task_relative_path.exists():
        return task_relative_path.resolve()

    raise FileNotFoundError(
        f"Could not find solution file: {solution_argument}"
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run public and hidden tests for one benchmark task."
    )

    parser.add_argument(
        "task_dir",
        type=Path,
        help="Path to the benchmark task directory.",
    )

    parser.add_argument(
        "--solution",
        type=str,
        default=None,
        help=(
            "Optional candidate solution file. The runner temporarily "
            "copies this file over starter.py."
        ),
    )

    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Run only the public tests.",
    )

    parser.add_argument(
        "--show-output",
        action="store_true",
        help="Show pytest output even when tests pass.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    task_dir = args.task_dir.expanduser().resolve()

    if not task_dir.is_dir():
        print(f"Error: task directory does not exist: {task_dir}")
        return 2

    starter_path = task_dir / "starter.py"

    if not starter_path.exists():
        print(f"Error: starter.py does not exist in {task_dir}")
        return 2

    try:
        solution_path = resolve_solution_path(
            args.solution,
            task_dir,
        )
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return 2

    # Save the exact original bytes so starter.py can always be restored.
    original_starter_contents = starter_path.read_bytes()

    print(f"Task: {task_dir.name}")

    if solution_path is None:
        print("Solution: current starter.py")
    else:
        print(f"Solution: {solution_path.name}")

    print()

    results: list[TestResult] = []

    try:
        if solution_path is not None:
            candidate_contents = solution_path.read_bytes()
            starter_path.write_bytes(candidate_contents)
            clear_python_cache(task_dir)

        public_result = run_test_suite(
            task_dir=task_dir,
            test_filename="test_public.py",
            suite_name="Public tests",
        )
        results.append(public_result)

        if not args.public_only:
            hidden_result = run_test_suite(
                task_dir=task_dir,
                test_filename="test_hidden.py",
                suite_name="Hidden tests",
            )
            results.append(hidden_result)

    finally:
        # Restore starter.py even if pytest crashes or an exception occurs.
        starter_path.write_bytes(original_starter_contents)
        clear_python_cache(task_dir)

    for result in results:
        print_result(result, args.show_output)

    overall_passed = all(result.passed for result in results)
    overall_status = "PASS" if overall_passed else "FAIL"

    print(f"Overall: {overall_status}")

    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())