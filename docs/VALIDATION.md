# Evidence and validation plan

## Near-term paid problem
A MagNav integrator needs a timestamped vector correction and uncertainty bound for external magnetic disturbance, sourced independently from the onboard navigation measurement. The buyer still needs a crustal map, absolute positioning from some initial/alternate source, platform magnetic calibration, and a way to assess spatial/temporal transfer error. A single magnetic sensor cannot disambiguate all of these.

## Prototype boundary
The Python baseline estimates a local reference-station vector residual, supports 1/5/15-minute leads, flags gross outliers, and exposes sigma as *model covariance*, not calibrated probability. The separate optional neural module yields B=curl(A), satisfying div(B)=0 mathematically for a smooth potential. It is not yet a genuine verified storm forecaster or autonomous spacecraft safe-mode controller.

## Data
- ESA Swarm VirES: https://vires.services/ and https://vires.services/hapi/ for magnetic residual and CHAOS model data. Verify ESA terms before any commercial use.
- NASA OMNI one-minute solar wind (time shifted to bow shock): https://data.nasa.gov/dataset/omni-1-min-data-set . It is useful as a potential leading driver but is not a local aircraft disturbance sensor.
- INTERMAGNET IAGA-2002 observatory files: https://intermagnet.org/data_download and https://intermagnet.org/data_formats.html . Default CC BY-NC 4.0 means get appropriate commercial rights; do not bundle their data in software products without permission.
- NOAA SWPC: https://www.swpc.noaa.gov/products-and-data ; be explicit about source latency and cadence.

This repository does not include, download automatically, or sublicense third-party datasets.

## Buyer-grade evaluation (required before claims)
1. Freeze an evaluation protocol *before* looking at test results. Record data provider, station ID and coordinates, cadence, source latency, and timestamps in UTC. Preserve missing samples and audit time alignment.
2. Split by disjoint storm events and by observatory geography, not random rows. Prevent temporal lookahead from scaling, quiet baselines, satellite ephemerides and labels. Use May 2024 as an example held-out severe storm event only when licensed data are available.
3. Score 1, 5, 15, 30-minute leads using vector RMSE, 95th percentile vector error, coverage of calibrated uncertainty intervals, detection delay, false-alarm rate, and compute/edge latency. Compare to persistence, seasonal/local-time baselines, and an independently implemented baseline model. IGRF/CHAOS internal reference fields alone are not valid short-horizon disturbance forecasting baselines.
4. Evaluate transient genuine storm onsets separately from single-station instrument spikes. The filter's innovation gate could erase a real event; stress-test and redesign before any flight-like use.
5. Validate correction spatial transfer using geographically separated observatories or actual magnetometer/IMU flights. Ground station error alone does not demonstrate navigation accuracy. Report position error only with a complete MagNav estimator.
6. Benchmark optional PINN against causal non-PINN models using the *same* permitted data and strict rolling-origin timing. The curl constraint is not evidence of improved accuracy.

## Proposed measurable customer gates (targets, not results)
- At least 15% lower **held-out** five-minute vector RMSE than persistence over predeclared evaluation strata, including storm periods; no hidden degradation on storm onset.
- An explicit calibrated uncertainty interval with measured empirical coverage and a fail-closed quality flag.
- Edge deployment profiling with reproducible latency, memory, and energy numbers on actual customer-class hardware.
- A pilot LOI contingent on real sensor feed availability, source rights, integration needs, and scope of responsibility.

## SAA and satellites: separate product evidence
Magnetic intensity and SAA morphology do not directly determine trapped proton/electron differential flux or dose rates. Satellite alerts need orbit/altitude/L-shell, particle data and an independently validated radiation environment model. Do not present this magnetic filter as a safe-mode trigger.

## Reporting rules
Do not call synthetic results a real-world benchmark. Do not claim NASA/Lockheed endorsement, certification, comparative speedup, TRL, proprietary rights to public datasets, or operational revenue without evidence.
