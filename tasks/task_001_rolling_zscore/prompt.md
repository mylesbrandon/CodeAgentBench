# Task 001: Rolling Z-Score

Implement `rolling_zscore(values, window)`.

The function takes a list of numbers and a positive integer `window`.

For each index `i`, compute the z-score of `values[i]` relative to the rolling window ending at `i`:

```python
values[max(0, i - window + 1): i + 1]