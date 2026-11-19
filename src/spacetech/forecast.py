"""Causal local geomagnetic disturbance estimation.

Input is a vector *disturbance residual* in nT from an independent ground
station / reference source (after subtracting a documented baseline).
It is not an absolute magnetic map nor an aircraft position estimator.
Samples are equally spaced. For gaps, explicitly pass None / NaNs;
never silently compress the time axis.
"""

from dataclasses import dataclass
import math
import numpy as np


def _vector(value, *, allow_missing=False):
    if value is None and allow_missing:
        return None
    v = np.asarray(value, dtype=float)
    if v.shape != (3,):
        raise ValueError("expected a three-component magnetic vector [X,Y,Z] in nT")
    if not np.all(np.isfinite(v)):
        if allow_missing:
            return None
        raise ValueError("magnetic vector contains non-finite values")
    return v


@dataclass(frozen=True)
class FieldForecast:
    mean_nT: np.ndarray
    sigma_nT: np.ndarray
    horizon_steps: int
    observations_accepted: int

    def __post_init__(self):
        if self.mean_nT.shape != (3,) or self.sigma_nT.shape != (3,):
            raise ValueError("forecast requires three components")


class CausalDisturbanceFilter:
    """Constant-velocity, 3-axis Kalman filter with conservative spike gating.

    The slope is a local empirical trend, not a physical core-dynamo model.
    A very abrupt, real geomagnetic disturbance can also trip the spike
    gate: this MUST be benchmarked on storm events before operational use.
    """

    def __init__(
        self,
        cadence_minutes=1.0,
        observation_sigma_nT=2.0,
        acceleration_sigma_nT_per_min2=0.30,
        initial_sigma_nT=15.0,
        spike_gate_sigma=8.0,
    ):
        vals = (
            cadence_minutes, observation_sigma_nT,
            acceleration_sigma_nT_per_min2, initial_sigma_nT,
            spike_gate_sigma,
        )
        if not all(np.isfinite(v) and v > 0 for v in vals):
            raise ValueError("filter parameters must be finite and positive")
        self.cadence_minutes = float(cadence_minutes)
        self.observation_sigma_nT = float(observation_sigma_nT)
        self.acceleration_sigma_nT_per_min2 = float(acceleration_sigma_nT_per_min2)
        self.initial_sigma_nT = float(initial_sigma_nT)
        self.spike_gate_sigma = float(spike_gate_sigma)
        self._state = None
        self._cov = None
        self.accepted = 0
        self.rejected = 0
        self.missing = 0

    def _transition(self, steps=1):
        dt = self.cadence_minutes * steps
        f = np.eye(6)
        f[:3, 3:] = np.eye(3) * dt
        q = self.acceleration_sigma_nT_per_min2 ** 2
        process = np.zeros((6, 6))
        process[:3, :3] = np.eye(3) * (q * dt**4 / 4)
        process[:3, 3:] = np.eye(3) * (q * dt**3 / 2)
        process[3:, :3] = process[:3, 3:]
        process[3:, 3:] = np.eye(3) * (q * dt**2)
        return f, process

    def update(self, observed_nT):
        """Assimilate one reference-station observation; return whether accepted."""
        obs = _vector(observed_nT, allow_missing=True)
        if self._state is None:
            if obs is None:
                self.missing += 1
                return False
            self._state = np.r_[obs, np.zeros(3)]
            a = self.initial_sigma_nT**2
            b = (self.initial_sigma_nT / self.cadence_minutes)**2
            self._cov = np.diag([a, a, a, b, b, b])
            self.accepted += 1
            return True

        f, q = self._transition()
        self._state = f @ self._state
        self._cov = f @ self._cov @ f.T + q
        if obs is None:
            self.missing += 1
            return False

        h = np.c_[np.eye(3), np.zeros((3, 3))]
        r = np.eye(3) * self.observation_sigma_nT**2
        innovation = obs - h @ self._state
        s = h @ self._cov @ h.T + r
        score = np.max(np.abs(innovation) / np.sqrt(np.diag(s)))
        if score > self.spike_gate_sigma:
            self.rejected += 1
            return False
        k = np.linalg.solve(s, h @ self._cov).T
        self._state = self._state + k @ innovation
        # Joseph covariance update preserves symmetry / nonnegative variance.
        i_kh = np.eye(6) - k @ h
        self._cov = i_kh @ self._cov @ i_kh.T + k @ r @ k.T
        self._cov = (self._cov + self._cov.T) / 2
        self.accepted += 1
        return True

    def forecast(self, horizon_steps=1):
        if self._state is None:
            raise ValueError("no valid reference observations yet")
        if isinstance(horizon_steps, bool) or not isinstance(horizon_steps, int) or horizon_steps < 0:
            raise ValueError("horizon_steps must be a nonnegative integer")
        # Propagate step by step so process-noise integration is consistent.
        x = self._state.copy()
        p = self._cov.copy()
        f, q = self._transition()
        for _ in range(horizon_steps):
            x = f @ x
            p = f @ p @ f.T + q
        return FieldForecast(
            mean_nT=x[:3].copy(),
            sigma_nT=np.sqrt(np.maximum(0.0, np.diag(p)[:3])),
            horizon_steps=horizon_steps,
            observations_accepted=self.accepted,
        )


def correct_magnetometer(raw_nT, disturbance, max_sigma_nT=50.0):
    """Subtract independent disturbance estimate; preserve crustal map signal.

    Fail closed on uncertain estimates. Uncertainty is model-based, NOT
    calibrated confidence / a certification of navigation accuracy.
    """
    raw = _vector(raw_nT)
    if not isinstance(disturbance, FieldForecast):
        raise TypeError("disturbance must be a FieldForecast from independent data")
    if not np.isfinite(max_sigma_nT) or max_sigma_nT <= 0:
        raise ValueError("max_sigma_nT must be positive")
    if not np.all(np.isfinite(disturbance.sigma_nT)):
        raise ValueError("invalid forecast uncertainty")
    if np.any(disturbance.sigma_nT > max_sigma_nT):
        raise ValueError("disturbance uncertainty exceeds correction limit")
    return raw - _vector(disturbance.mean_nT)


def _rmse_and_p95(predictions, targets):
    if not predictions:
        return {"rmse_vector_nT": None, "p95_vector_error_nT": None}
    error = np.asarray(predictions) - np.asarray(targets)
    norms = np.linalg.norm(error, axis=1)
    return {
        "rmse_vector_nT": float(np.sqrt(np.mean(norms**2))),
        "p95_vector_error_nT": float(np.quantile(norms, 0.95)),
    }


def benchmark_forecasts(observations_nT, horizon_steps=5, warmup_steps=30,
                        evaluation_targets_nT=None, **filter_kwargs):
    """Causal rolling-origin hindcast vs persistence (not a fitted oracle).

    Ground truth may be supplied ONLY for a synthetic validation study;
    in a real dataset, scoring uses future observed readings. Input cadence
    is uniform and missing periods remain explicit NaN rows.
    """
    data = np.asarray(observations_nT, dtype=float)
    if data.ndim != 2 or data.shape[1] != 3:
        raise ValueError("observations must be an N x 3 array")
    if not isinstance(horizon_steps, int) or horizon_steps < 1:
        raise ValueError("horizon_steps must be a positive integer")
    if not isinstance(warmup_steps, int) or warmup_steps < 1:
        raise ValueError("warmup_steps must be a positive integer")
    truth = data if evaluation_targets_nT is None else np.asarray(evaluation_targets_nT, dtype=float)
    if truth.shape != data.shape:
        raise ValueError("targets must match observation shape")

    kf = CausalDisturbanceFilter(**filter_kwargs)
    predicted, persisted, targets = [], [], []
    for i in range(len(data) - horizon_steps):
        v = data[i]
        kf.update(v)
        target = truth[i + horizon_steps]
        if i + 1 < warmup_steps or not np.all(np.isfinite(v)) or not np.all(np.isfinite(target)):
            continue
        if not kf.accepted:
            continue
        predicted.append(kf.forecast(horizon_steps).mean_nT)
        persisted.append(v.copy())
        targets.append(target.copy())
    model_metrics = _rmse_and_p95(predicted, targets)
    baseline_metrics = _rmse_and_p95(persisted, targets)
    m, b = model_metrics["rmse_vector_nT"], baseline_metrics["rmse_vector_nT"]
    skill = None if not b else 1.0 - m / b
    return {
        "horizon_steps": horizon_steps,
        "evaluated_origins": len(predicted),
        "filter": model_metrics,
        "persistence": baseline_metrics,
        "skill_vs_persistence": skill,
        "accepted_observations": kf.accepted,
        "rejected_observations": kf.rejected,
        "missing_observations": kf.missing,
        "target_kind": "observed" if evaluation_targets_nT is None else "synthetic_latent_truth",
    }


def generate_synthetic_disturbance(count=720, seed=42):
    """Uniform-in-space, hence divergence-free synthetic time variation.

    No claim this emulates real magnetosphere dynamics, sensor spatial
    decorrelation, timing delays, hard/soft iron, or aircraft maneuvers.
    """
    if count < 50:
        raise ValueError("count must be at least 50")
    rng = np.random.default_rng(seed)
    t = np.arange(count, dtype=float)
    smooth = np.column_stack([
        16 * np.sin(t / 65) + 10 * np.sin(t / 19),
        -12 * np.sin(t / 84 + 0.7),
        8 * np.cos(t / 49),
    ])
    burst = (22 * np.exp(-0.5 * ((t - count * 0.63) / 14) ** 2))[:, None]
    truth = smooth + burst * np.array([1.0, -0.45, 0.2])
    noisy = truth + rng.normal(0.0, 2.0, size=truth.shape)
    indices = rng.choice(np.arange(10, count), size=max(1, count // 140), replace=False)
    noisy[indices] += rng.choice([-1.0, 1.0], size=(len(indices), 3)) * 80
    gaps = rng.choice(np.arange(10, count), size=max(1, count // 170), replace=False)
    noisy[gaps] = np.nan
    return noisy, truth
