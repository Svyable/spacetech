# SpaceTech

Open engineering workbench for **geomagnetic disturbance estimation and magnetic-navigation resilience**.

## Mission
Build testable, commercially useful software for magnetic-navigation interference correction, short-horizon anomaly prediction, and (later) ground-sensor network operations. The near-term objective is to establish a reproducible benchmark, not claim an operational safety product.

## Product sequence
1. **MagNav disturbance layer**: estimate local external magnetic disturbance and uncertainty from a reference station or other independent observations, then correct navigation magnetometer vectors.
2. **Physics-informed forecasting**: evaluate causal time-series baselines against a Maxwell-constrained learned vector field.
3. **Sensor mesh**: provenance-aware station ingestion, quality control, and latency monitoring before buying hardware.

## Scientific guardrails
- The Earth's core dynamo need not be modeled to predict *short-term external disturbance*, but no algorithm can separate unknown position, crustal field, aircraft bias, and global disturbances from a single magnetic vector without additional information.
- The constraint `div(B)=0` alone does **not** establish forecasting skill.
- A geomagnetic intensity map is **not** a spacecraft radiation-dose forecast. SAA radiation use cases require energetic particle observations and separate hazard models.
- Operational or flight use requires extensive independent validation and safety review.

## Data and rights
- ESA Swarm / VirES: https://vires.services/ (review ESA terms and collection eligibility)
- NASA OMNI 1-minute: https://data.nasa.gov/dataset/omni-1-min-data-set
- INTERMAGNET: https://intermagnet.org/data_download (normally CC BY-NC 4.0; do **not** use for commercial training, redistribution, or service delivery without suitable rights)

## Status
Research-stage repository. No claim of operational accuracy, TRL advancement, secured procurement, or fielded capabilities. See upcoming prototype and evaluation artifacts in pull requests.
