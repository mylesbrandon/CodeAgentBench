# Running CodeAgentBench-Lite

## Candidate solution sets

A solution set contains one Python candidate per benchmark task.

Example:

```text
results/candidates/reference/
├── task_001.py
└── task_002.py
```

Candidate filenames must match the `task_id` in each task's
`metadata.json`.

## Run one task

```bash
python runner/run_task.py \
  --task tasks/task_001_rolling_zscore \
  --solution results/candidates/reference/task_001.py \
  --model reference \
  --condition validation
```

## Run the full benchmark

```bash
python runner/run_benchmark.py \
  --solution-set results/candidates/reference \
  --model reference \
  --condition validation
```

## Individual run artifacts

Each attempted task produces a directory under:

```text
results/runs/<task_id>/<run_id>/
```

It contains:

* `result.json`
* `candidate_snapshot.py`
* `prompt.md`
* `public_test_output.txt`
* `hidden_test_output.txt`

## Aggregate results

Each full benchmark run creates:

```text
results/summaries/<model>_<condition>_results.csv
results/summaries/<model>_<condition>_summary.json
```

## Metrics

### Public pass rate

The fraction of benchmark tasks for which the candidate passes all
public tests.

### Hidden pass rate

The fraction of benchmark tasks for which the candidate passes all
hidden tests.

### Overall pass rate

The fraction of benchmark tasks for which the candidate passes both
public and hidden tests.

### Public-hidden gap

```text
public pass rate - hidden pass rate
```

A large gap suggests that candidate solutions pass obvious examples
but fail less visible edge cases.

## Missing candidates

If a solution set does not contain a candidate for a task, the batch
runner records the task as `missing_candidate`.

Missing candidates count as unsolved in aggregate pass rates, but they
remain distinct from attempted candidates that failed.
