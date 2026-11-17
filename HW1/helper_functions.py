"""Bass curves and estimation. Time is measured in years."""

from itertools import product

import numpy as np
from scipy.optimize import least_squares


def bass_cumulative(t, p, q, market):
    t = np.asarray(t, dtype=float)
    decay = np.exp(-(p + q) * t)
    return market * (-np.expm1(-(p + q) * t)) / (1 + (q / p) * decay)


def bass_from_seed(t, p, q, market, initial):
    """Exact Bass solution with cumulative adoption initial at t=0."""
    if not (0 <= initial < market and p > 0 and q > 0):
        raise ValueError("Need 0 <= initial < market, and positive p and q")
    fraction = initial / market
    ratio = (p + q * fraction) / (1 - fraction)
    decay = np.exp(-(p + q) * np.asarray(t, dtype=float))
    return market * (ratio - p * decay) / (ratio + q * decay)


def fit_bass(years, penetration, origin=1967):
    """Estimate p, q and saturation share, giving each survey equal weight."""
    times = np.asarray(years, dtype=float) - origin
    observed = np.asarray(penetration, dtype=float)
    candidates = []
    for p0, q0, saturation0 in product([0.0001, 0.001, 0.01], [0.15, 0.4], [0.85, 0.98]):
        fit = least_squares(
            lambda b: bass_cumulative(times, *b) - observed,
            x0=[p0, q0, saturation0],
            bounds=([1e-8, 1e-8, 0.5], [1.0, 2.0, 1.0]),
            xtol=1e-12, ftol=1e-12, gtol=1e-12,
            max_nfev=10000,
        )
        if fit.success:
            candidates.append(fit)
    if not candidates:
        raise RuntimeError("No Bass fit converged")
    best = min(candidates, key=lambda result: np.sum(result.fun ** 2))
    return best.x


def rmse(actual, predicted):
    return float(np.sqrt(np.mean((np.asarray(actual) - np.asarray(predicted)) ** 2)))
