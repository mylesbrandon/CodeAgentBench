from runner.evaluation import build_summary


def test_summary_metrics():
    results = [
        {
            "status": "attempted",
            "category": "numerical",
            "public_passed": True,
            "hidden_passed": False,
            "overall_passed": False,
        },
        {
            "status": "attempted",
            "category": "algorithms",
            "public_passed": True,
            "hidden_passed": True,
            "overall_passed": True,
        },
    ]

    summary = build_summary(
        results,
        model="test-model",
        condition="one_shot",
    )

    assert summary["task_count"] == 2
    assert summary["attempted_count"] == 2
    assert summary["missing_count"] == 0
    assert summary["public_pass_rate"] == 1.0
    assert summary["hidden_pass_rate"] == 0.5
    assert summary["overall_pass_rate"] == 0.5
    assert summary["public_hidden_gap"] == 0.5

    assert summary["category_results"]["numerical"] == {
        "tasks": 1,
        "attempted": 1,
        "passed": 0,
    }

    assert summary["category_results"]["algorithms"] == {
        "tasks": 1,
        "attempted": 1,
        "passed": 1,
    }
