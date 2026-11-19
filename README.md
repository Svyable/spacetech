# SpaceTech

**Geomagnetic disturbance intelligence for navigation and spacecraft operations.**

SpaceTech is a research-stage engineering workbench aimed at commercial aerospace customers. The first prototype estimates **external geomagnetic vector disturbance** from an independent reference source and evaluates short-horizon forecasts. The goal is to produce buyer-grade evidence, not to simulate the Earth's core for a century.

## Current code (v0.1.0)

- A causal, 3-axis Kalman trend filter for disturbance residuals in nanotesla (nT).
- Explicit minute gaps, spike gating, propagated model uncertainty, and a fail-closed correction interface.
- An IAGA-2002 XYZ observatory loader (not HDZ), with UTC minute reindexing and missing-value handling.
- A reproducible rolling-origin benchmark against persistence.
- An optional PyTorch vector-potential neural field: B = curl(A), ensuring div(B) = 0 for a smooth A. **This is a research field representation, not a validated dynamic forecasting PINN.**
- Pytest and GitHub Actions for Python 3.11/3.12.

## Quickstart

Requirements: Python 3.10+.

~~~bash
python -m pip install -e ".[dev]"
python -m pytest -q
spacetech --demo --horizon 5
~~~

The demo creates a fixed-seed *synthetic* uniform-in-space, divergence-free disturbance with artificial sensor spikes and gaps. It compares against a persistence forecast using latent simulated truth. These scores **do not measure real flight, storm or satellite performance**.

For a locally supplied IAGA-2002 XYZ **minute** file (verify applicable use rights):

~~~bash
spacetech --iaga path/to/your-file.min --horizon 5
~~~

The IAGA workflow subtracts its first valid vector as a reference. That is useful for reproducible prototype evaluation, **not** a validated quiet-time baseline or separation of external/internal fields.

Optional neural-field tests:

~~~bash
python -m pip install -e ".[dev,pinn]"
python -m pytest tests/test_pinn.py -q
~~~

No data are automatically fetched or bundled. All scripts are research-use software and not flight-qualified.

## Product sequence

| Track | Customer decision | Evidence gate |
| --- | --- | --- |
| 1. Magnetic navigation correction | Is an independently sourced disturbance estimate reducing navigation error? | Time-, event- and geography-held-out magnetic errors, then aircraft position error |
| 2. Physics-constrained short-horizon forecast | Does a learned model beat strong causal baselines with honest latency? | 1/5/15/30-minute out-of-event scores, storm onset and uncertainty calibration |
| 3. Ground magnetic sensor mesh | Can a regional feed meet cost, latency and data-quality requirements? | Clock synchronization, calibration, multi-site pilot and rights-cleared observations |
| Separate: SAA radiation | Can particle-specific hazard prediction reduce costly false safe-mode hours? | Orbit-aware proton/electron flux and dose validation, **not** magnetic strength alone |

See [the evidence plan](docs/VALIDATION.md), [commercialization discovery](docs/COMMERCIAL.md), and [open milestones](https://github.com/Svyable/spacetech/issues).

## Scientific and commercial guardrails

- One magnetometer alone cannot disentangle unknown aircraft position, crustal map error, platform bias and external disturbance. Reference measurements, calibration and appropriate navigation fusion are required.
- A divergence-free magnetic field is not automatically a useful forecast; this repo does not yet demonstrate real storm or flight performance.
- A moving magnetic anomaly is not a spacecraft radiation-dose forecast. SAA particle flux requires a separate model and observations.
- Do not compare a five-minute weather forecast only to IGRF/CHAOS internal-field references; include fair causal disturbance baselines.
- Source rights matter. [INTERMAGNET](https://intermagnet.org/data_conditions.html) generally uses CC BY-NC 4.0 and needs additional permission for commercial use. Check [ESA VirES terms](https://vires.services/) and NASA/NOAA feed-specific rules separately.
- A public repository without an explicit license does not grant blanket commercial reuse or ownership of third-party data.

## Provenance and maturity

The first CI-gated prototype was delivered in [PR #1](https://github.com/Svyable/spacetech/pull/1). No endorsement, customer contract, procurement win, operational accuracy, TRL advancement or proprietary dataset rights are implied. No code in this repository should autonomously command spacecraft safe mode or flight navigation.
