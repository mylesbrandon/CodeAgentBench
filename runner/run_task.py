from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TestResult:
    """Stores the result of one pytest test suite."""

    name: str
    passed: bool
    return_code: int
    duration_seconds: float
    output: str
    passed_count: int
    total_count: int
    failed_tests: list[str]


PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
            passed_count=0,
            total_count=0,
            failed_tests=[],
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
            "-p",
            "no:cacheprovider",
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
    raw_output = "\n".join(part for part in output_parts if part)
    output = "\n".join(
        line.rstrip()
        for line in raw_output.splitlines()
    )

    outcome_matches = re.findall(
        r"(\d+) (passed|failed|errors?|skipped|xfailed|xpassed)"
        r"(?=,|\s+in\s|$)",
        output,
        flags=re.MULTILINE,
    )
    passed_count = sum(
        int(value)
        for value, outcome in outcome_matches
        if outcome == "passed"
    )
    total_count = sum(int(value) for value, _ in outcome_matches)
    failed_tests = re.findall(
        r"^FAILED\s+([^\s]+)",
        output,
        flags=re.MULTILINE,
    )

    return TestResult(
        name=suite_name,
        passed=completed_process.returncode == 0,
        return_code=completed_process.returncode,
        duration_seconds=duration,
        output=output,
        passed_count=passed_count,
        total_count=total_count,
        failed_tests=failed_tests,
    )


def safe_identifier(value: str) -> str:
    """Convert a user-facing run label into a filesystem-safe identifier."""
    identifier = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return identifier.strip("._-") or "unspecified"


def portable_path(path: Path) -> str:
    """Return a project-relative path when possible."""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def create_run_directory(
    task_id: str,
    model: str,
    condition: str,
    timestamp: datetime,
) -> tuple[str, Path]:
    """Create a unique result directory for a benchmark evaluation."""
    timestamp_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    base_run_id = "_".join(
        (
            timestamp_id,
            safe_identifier(model),
            safe_identifier(condition),
        )
    )
    task_runs_dir = PROJECT_ROOT / "results" / "runs" / task_id
    task_runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = base_run_id
    suffix = 2
    run_dir = task_runs_dir / run_id

    while run_dir.exists():
        run_id = f"{base_run_id}_{suffix}"
        suffix += 1
        run_dir = task_runs_dir / run_id

    run_dir.mkdir()
    return run_id, run_dir


def suite_record(result: TestResult, output_filename: str) -> dict:
    """Build the serializable result record for one test suite."""
    return {
        "status": "pass" if result.passed else "fail",
        "passed": result.passed_count,
        "total": result.total_count,
        "duration_seconds": round(result.duration_seconds, 3),
        "output": output_filename,
        "failed_tests": result.failed_tests,
    }


def write_run_artifacts(
    task_dir: Path,
    solution_path: Path | None,
    candidate_contents: bytes,
    model: str,
    condition: str,
    results: list[TestResult],
) -> Path:
    """Persist a reproducible snapshot and structured result for one run."""
    metadata_path = task_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    task_id = metadata["task_id"]
    timestamp = datetime.now().astimezone()
    run_id, run_dir = create_run_directory(
        task_id=task_id,
        model=model,
        condition=condition,
        timestamp=timestamp,
    )

    results_by_name = {result.name: result for result in results}
    public_result = results_by_name["Public tests"]
    hidden_result = results_by_name.get("Hidden tests")

    public_output_name = "public_test_output.txt"
    hidden_output_name = "hidden_test_output.txt"
    (run_dir / public_output_name).write_text(
        f"{public_result.output}\n",
        encoding="utf-8",
    )
    (run_dir / hidden_output_name).write_text(
        (
            f"{hidden_result.output}\n"
            if hidden_result is not None
            else "Not run (--public-only).\n"
        ),
        encoding="utf-8",
    )
    shutil.copyfile(task_dir / "prompt.md", run_dir / "prompt.md")
    (run_dir / "candidate_snapshot.py").write_bytes(candidate_contents)

    tests = {
        "public": suite_record(public_result, public_output_name),
        "hidden": (
            suite_record(hidden_result, hidden_output_name)
            if hidden_result is not None
            else {
                "status": "skipped",
                "passed": 0,
                "total": 0,
                "duration_seconds": 0.0,
                "output": hidden_output_name,
                "failed_tests": [],
            }
        ),
    }
    overall_passed = all(result.passed for result in results)
    candidate_source = solution_path or (task_dir / "starter.py")
    result_document = {
        "schema_version": 1,
        "run_id": run_id,
        "timestamp": timestamp.isoformat(timespec="seconds"),
        "task": {
            "id": task_id,
            "name": metadata["name"],
            "path": portable_path(task_dir),
        },
        "candidate": {
            "id": safe_identifier(model),
            "model": model,
            "condition": condition,
            "path": portable_path(candidate_source),
        },
        "tests": tests,
        "overall_status": "pass" if overall_passed else "fail",
        "failure_category": None if overall_passed else "test_failure",
    }
    (run_dir / "result.json").write_text(
        json.dumps(result_document, indent=2) + "\n",
        encoding="utf-8",
    )

    failed_tests = [
        failed_test
        for result in results
        for failed_test in result.failed_tests
    ]
    failed_test_text = (
        "\n".join(f"- `{test_name}`" for test_name in failed_tests)
        if failed_tests
        else "- None"
    )
    analysis = (
        f"# Run Analysis: {task_id}\n\n"
        f"- Candidate: `{model}`\n"
        f"- Condition: `{condition}`\n"
        f"- Public tests: {tests['public']['status'].upper()} "
        f"({tests['public']['passed']}/{tests['public']['total']})\n"
        f"- Hidden tests: {tests['hidden']['status'].upper()} "
        f"({tests['hidden']['passed']}/{tests['hidden']['total']})\n"
        f"- Overall: {result_document['overall_status'].upper()}\n\n"
        "## Failed tests\n\n"
        f"{failed_test_text}\n"
    )
    (run_dir / "analysis.md").write_text(analysis, encoding="utf-8")

    return run_dir


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

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=(
            "Candidate or model label recorded with the evaluation. "
            "Defaults to the solution filename."
        ),
    )

    parser.add_argument(
        "--condition",
        type=str,
        default="unspecified",
        help="Evaluation condition recorded with the run artifacts.",
    )

    parser.add_argument(
        "--no-record",
        action="store_true",
        help="Run the evaluation without writing a result directory.",
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
    candidate_contents = (
        solution_path.read_bytes()
        if solution_path is not None
        else original_starter_contents
    )
    model = args.model or (
        solution_path.stem
        if solution_path is not None
        else "starter"
    )

    print(f"Task: {task_dir.name}")

    if solution_path is None:
        print("Solution: current starter.py")
    else:
        print(f"Solution: {solution_path.name}")

    print()

    results: list[TestResult] = []

    try:
        if solution_path is not None:
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

    if not args.no_record:
        run_dir = write_run_artifacts(
            task_dir=task_dir,
            solution_path=solution_path,
            candidate_contents=candidate_contents,
            model=model,
            condition=args.condition,
            results=results,
        )
        print(f"Run artifacts: {portable_path(run_dir)}")

    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
