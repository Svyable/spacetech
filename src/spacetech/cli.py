"""Minimal reproducible bench CLI. No automatic downloads, no data resale."""
import argparse
import json
import numpy as np

from .data import load_iaga2002_xyz
from .forecast import benchmark_forecasts, generate_synthetic_disturbance


def main(argv=None):
    p = argparse.ArgumentParser(description="Causal geomagnetic disturbance forecast benchmark")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="synthetic, not real-world evidence")
    source.add_argument("--iaga", help="IAGA-2002 XYZ minute file; confirm data rights")
    p.add_argument("--horizon", type=int, default=5, help="forecast lead time in samples (1 min)")
    p.add_argument("--warmup", type=int, default=30)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)
    if args.demo:
        data, truth = generate_synthetic_disturbance(seed=args.seed)
        result = benchmark_forecasts(data, args.horizon, args.warmup, truth)
        result["source"] = "synthetic_simulation_not_operational_evidence"
        result["seed"] = args.seed
    else:
        times, data = load_iaga2002_xyz(args.iaga)
        # Subtract an initial reference for small residuals. A real production
        # pipeline needs a documented quiet-time baseline and geolocation.
        valid = np.flatnonzero(np.isfinite(data).all(axis=1))
        if len(valid) == 0:
            p.error("no finite XYZ samples")
        residual = data - data[valid[0]]
        result = benchmark_forecasts(residual, args.horizon, args.warmup)
        result["source"] = "iaga_observed_data_research_only"
        result["utc_start"] = times[0].isoformat()
        result["utc_end"] = times[-1].isoformat()
        result["baseline_method"] = "first_finite_sample_only_not_quiet_time_model"
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
