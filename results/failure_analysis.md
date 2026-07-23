# Failure Analysis Notes

## Task 001: Rolling Z-Score

This task evaluates whether an agent can implement a numerical rolling statistic robustly, not merely pass the obvious increasing-sequence case.

The public tests check basic behavior: simple rolling z-score computation and invalid window handling.

The hidden tests target common shallow-implementation failures:

- division by zero when the rolling standard deviation is zero
- incorrect handling of NaN values
- using the full history instead of the rolling window
- using sample standard deviation instead of population standard deviation
- failing when the window is larger than the input
- failing on negative values or degenerate inputs

This task is useful because many generated solutions can appear correct on simple examples while failing numerical edge cases.

### Manual Validation

To verify that Task 001 distinguishes robust implementations from superficially correct ones, I evaluated three deliberately flawed implementations. Each implementation represented a common mistake that an LLM coding agent might make.

1. Missing zero-variance handling

This implementation correctly computed the rolling mean and standard deviation but did not check whether the standard deviation was zero before dividing.

Public tests: PASS
Hidden tests: FAIL
Detected by: test_constant_sequence_zero_variance
Observed failure: The implementation attempted to divide by zero when the rolling window contained identical values.
Failure category: Numerical edge case / zero-variance handling

This result shows that the public tests were not sufficient to detect the error, while the hidden constant-sequence test successfully identified it.

2. Full-history instead of rolling-window implementation

This implementation calculated each z-score using every value from the beginning of the sequence through the current position rather than using only the specified rolling window.

Public tests: PASS
Hidden tests: FAIL
Detected by: test_uses_rolling_window_not_full_history
Observed failure: The implementation returned an incorrect z-score for the final value in [1, 2, 100, 101] because earlier values remained in the calculation.
Failure category: Specification misunderstanding / incorrect window selection

This result demonstrates that a solution can pass simple examples while still implementing the wrong statistical procedure.

3. Missing NaN handling

This implementation attempted to compute statistics directly over every value in the rolling window without filtering out NaN values or separately handling a current value that was NaN.

Public tests: PASS
Hidden tests: FAIL
Detected by:
test_nan_current_value_returns_nan
test_nan_ignored_in_window
test_all_nan_input
Observed failure: NaN values propagated through the mean and standard-deviation calculations, producing incorrect or undefined results for later positions.
Failure category: Missing-value handling / numerical robustness

This result shows that basic correctness tests do not adequately measure robustness when inputs contain missing numerical values.

Validation Conclusion

All three deliberately flawed implementations passed the basic public tests but failed one or more targeted hidden tests. This suggests that the hidden test suite adds meaningful discriminatory power rather than merely repeating the public test coverage.

The validation also confirms that Task 001 measures several distinct capabilities:

adherence to rolling-window semantics
handling of degenerate numerical cases
correct treatment of missing values
robustness beyond basic example inputs

Future validation should include additional flawed implementations, such as one that uses sample standard deviation instead of population standard deviation and one that mishandles windows larger than the input sequence.

## Task 002: Shortest Path

### Capability being evaluated

Task 002 evaluates algorithmic debugging, edge relaxation, priority-queue reasoning, and robust handling of graph edge cases.

### Controlled baseline results

#### Reference solution

- Public tests: PASS (5/5)
- Hidden tests: PASS (8/8)
- Expected outcome: all tests pass.

#### No-relaxation-check baseline

- Public tests: PASS (5/5)
- Hidden tests: FAIL (4/8 passed)
- Failed tests: `test_unreachable_target`, `test_duplicate_edges_choose_cheapest`, `test_node_with_empty_adjacency_list`, `test_graph_is_directed`
- Main failure: the implementation can overwrite a shorter distance with a longer distance. Because this controlled baseline is the flawed starter, it also retains the starter's incorrect unreachable-path return value.

#### Unreachable-returns-None baseline

- Public tests: PASS (5/5)
- Hidden tests: FAIL (5/8 passed)
- Failed tests: `test_unreachable_target`, `test_node_with_empty_adjacency_list`, `test_graph_is_directed`
- Main failure: the implementation violates the specified unreachable-path return format.

### Benchmark conclusion

The task distinguishes basic shortest-path behavior from robust implementation. Public tests establish the normal contract, while hidden tests detect plausible defects involving duplicate edges and unreachable nodes.

## Task 003: Lookahead-Safe Signal Alignment

### Capability being evaluated

Task 003 evaluates time-series alignment and leakage prevention. The
return from index `t - 1` to index `t` uses `signals[t - 1]` because
that is the latest position known before the price movement occurs.
Using `signals[t]` would let a strategy act on an already-realized
return.

Transaction costs use the same timing convention. The initial
position is free, and later output indices deduct:

```text
transaction_cost * abs(signals[t - 1] - signals[t - 2])
```

### Controlled baseline results

#### Reference solution

- Public tests: PASS (6/6)
- Hidden tests: PASS (10/10)

#### Current-signal lookahead baseline

- Public tests: PASS (6/6)
- Hidden tests: FAIL (5/10 passed)
- Detected failures: earning a price jump after its signal, using the
  opposite current signal, and misaligning turnover costs.

#### Ignores-transaction-costs baseline

- Public tests: PASS (6/6)
- Hidden tests: FAIL (7/10 passed)
- Detected failures: cost timing, turnover-size cost, and costs on flat
  prices.

#### Flat-trade-cost baseline

- Public tests: PASS (6/6)
- Hidden tests: FAIL (8/10 passed)
- Detected failures: position changes larger than one unit are charged
  a flat fee instead of proportional turnover.

### Benchmark conclusion

All controlled defects pass the public examples, while the hidden
suite distinguishes lookahead leakage from two different
transaction-cost mistakes. This keeps the task focused on causal
alignment while still testing a realistic consequence of position
changes.
