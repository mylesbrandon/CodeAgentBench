from __future__ import annotations

import argparse
from pathlib import Path

if __package__:
    from .evaluation import evaluate_candidate
else:
    from evaluation import evaluate_candidate


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate one benchmark task."
    )

    parser.add_argument(
        "--task",
        required=True,
        type=Path,
        help="Path to the benchmark task directory.",
    )

    parser.add_argument(
        "--solution",
        required=True,
        type=Path,
        help="Path to the candidate Python solution.",
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Model or baseline name.",
    )

    parser.add_argument(
        "--condition",
        required=True,
        help="Evaluation condition, such as one_shot.",
    )

    parser.add_argument(
        "--results-root",
        type=Path,
        default=Path("results"),
        help="Directory where run artifacts are stored.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    result = evaluate_candidate(
        task_path=args.task,
        solution_path=args.solution,
        model=args.model,
        condition=args.condition,
        results_root=args.results_root,
    )

    print(f"Task: {result['task_id']} — {result['task_name']}")
    print(f"Model: {result['model']}")
    print(f"Condition: {result['condition']}")
    print(
        "Public tests:",
        "PASS" if result["public_passed"] else "FAIL",
    )
    print(
        "Hidden tests:",
        "PASS" if result["hidden_passed"] else "FAIL",
    )
    print(
        "Overall:",
        "PASS" if result["overall_passed"] else "FAIL",
    )
    print(f"Run artifacts: {result['run_path']}")


if __name__ == "__main__":
    main()
