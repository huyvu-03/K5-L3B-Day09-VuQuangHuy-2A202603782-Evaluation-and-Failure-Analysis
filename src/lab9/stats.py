"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import comb, isfinite

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class
LABELS = frozenset({"FAIL", "PASS"})


def _paired_labels(human: Sequence[str], judge: Sequence[str]) -> tuple[Sequence[str], Sequence[str]]:
    if len(human) != len(judge):
        raise ValueError("human and judge label sequences must have the same length")
    if any(label not in LABELS for label in human):
        raise ValueError("human labels must be 'PASS' or 'FAIL'")
    if any(label not in LABELS for label in judge):
        raise ValueError("judge labels must be 'PASS' or 'FAIL'")
    return human, judge


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    human, judge = _paired_labels(human, judge)
    tp = fp = fn = tn = 0
    for truth, prediction in zip(human, judge):
        if truth == POS and prediction == POS:
            tp += 1
        elif truth != POS and prediction == POS:
            fp += 1
        elif truth == POS and prediction != POS:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    counts = confusion(human, judge)
    precision_denominator = counts["tp"] + counts["fp"]
    recall_denominator = counts["tp"] + counts["fn"]
    precision = counts["tp"] / precision_denominator if precision_denominator else 0.0
    recall = counts["tp"] / recall_denominator if recall_denominator else 0.0
    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    human, judge = _paired_labels(human, judge)
    n = len(human)
    if n == 0:
        raise ValueError("Cohen's kappa is undefined for empty labels")

    observed = sum(truth == prediction for truth, prediction in zip(human, judge)) / n
    human_fail_rate = sum(label == POS for label in human) / n
    judge_fail_rate = sum(label == POS for label in judge) / n
    expected = (human_fail_rate * judge_fail_rate
                + (1.0 - human_fail_rate) * (1.0 - judge_fail_rate))
    if expected == 1.0:
        raise ValueError("Cohen's kappa is undefined when expected agreement is 1")
    return (observed - expected) / (1.0 - expected)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    rates = (observed_rate, sensitivity, specificity)
    if any(not isfinite(rate) or not 0.0 <= rate <= 1.0 for rate in rates):
        raise ValueError("observed rate, sensitivity, and specificity must be finite rates in [0, 1]")
    denominator = sensitivity + specificity - 1.0
    if denominator == 0.0:
        raise ValueError("Rogan-Gladen correction is undefined when sensitivity + specificity = 1")
    corrected = (observed_rate + specificity - 1.0) / denominator
    return min(1.0, max(0.0, corrected))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    if len(a) != len(b):
        raise ValueError("paired samples must have the same length")
    if not a:
        raise ValueError("paired bootstrap requires at least one item")
    if n_resamples < 1:
        raise ValueError("n_resamples must be positive")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be strictly between 0 and 1")
    if any(not isfinite(float(value)) for value in (*a, *b)):
        raise ValueError("paired samples must contain only finite values")
    if all(x == y for x, y in zip(a, b)):
        return 0.0, 0.0, 0.0

    import numpy as np
    from scipy.stats import bootstrap

    def mean_difference(x, y, axis=-1):
        return np.mean(x - y, axis=axis)

    result = bootstrap(
        (np.asarray(a, dtype=float), np.asarray(b, dtype=float)),
        mean_difference,
        paired=True,
        vectorized=True,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method="percentile",
        rng=np.random.default_rng(rng),
    )
    difference = float(np.mean(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)))
    return difference, float(result.confidence_interval.low), float(result.confidence_interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    _validate_pass_k_args(n, c, k)
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    _validate_pass_k_args(n, c, k)
    return comb(c, k) / comb(n, k)


def _validate_pass_k_args(n: int, c: int, k: int) -> None:
    if any(not isinstance(value, int) or isinstance(value, bool) for value in (n, c, k)):
        raise ValueError("n, c, and k must be integers")
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= c <= n:
        raise ValueError("c must be between 0 and n")
    if not 1 <= k <= n:
        raise ValueError("k must be between 1 and n")
