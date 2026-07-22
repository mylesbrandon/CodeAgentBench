from pathlib import Path

from runner.evaluation import discover_tasks


def test_discovers_task_directories_in_order(
    tmp_path: Path,
):
    (tmp_path / "task_002_second").mkdir()
    (tmp_path / "task_001_first").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "README.md").write_text(
        "not a task",
        encoding="utf-8",
    )

    discovered = discover_tasks(tmp_path)

    assert [path.name for path in discovered] == [
        "task_001_first",
        "task_002_second",
    ]
