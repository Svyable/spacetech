# Commercialization discovery

## Initial offer
Research prototype -> integration test -> paid evaluation of **MagNav external disturbance estimation** for a qualified navigation or magnetometer integrator. Deliverable: a reference-station-driven disturbance time series, causal forecast, uncertainty/quality indicators, reproducible benchmark package, latency report and API specification. Customer must supply the aircraft/sensor integration context.

## Buyer conversations before extra model complexity
- Ask aerospace navigation integrators which error dominates their magnetic fix budget: platform hard/soft-iron drift, crustal map uncertainty, external magnetic weather, or sensor noise. Our first wedge addresses external disturbance only.
- Ask satellite bus/magnetometer vendors whether platform self-field calibration is higher priority than MagNav. If so, build a separate onboard calibration branch with Helmholtz-coil reproducibility and attitude-conditioned regressors; do not confl​ate it with geospace changes.
- Ask NOAA/NASA space-weather operators which *decision* improves from short-lead station corrections (not merely a pretty field plot), and what latency, false-alarm and validation evidence they require.
- Ask two pilot prospects for an anonymized sensor log and approval to measure integration performance. No inbound buyer or partnership is yet confirmed.

## Procurement pathways (leads, not commitments)
- NASA 2026 SBIR/STTR information: https://www.nasa.gov/sbir_sttr/nasa-sbir-sttr-program-program-year-2026-information-hub/ . NASA's 2026 program uses Broad Agency Announcement appendices; verify current topics, eligibility and dates rather than assuming an open call or guaranteed award.
- NASA solicitations: https://www.nasa.gov/sbir_sttr/submissions/
- Lockheed Martin Space procurement: https://www.lockheedmartin.com/en-us/suppliers/business-area-procurement/space.html
- Other possible buyers: quantum magnetometer OEMs, navigation software integrators, CubeSat builders, and commercial space-weather data providers.

## IP and third-party content
Public repository publication does not establish ownership of novel inventions, trade secrets, or exclusive IP. No source-code license is granted by default. Before a commercial contract: confirm contributor ownership, government-funded data rules, supplier cybersecurity requirements, and third-party data rights. INTERMAGNET default CC BY-NC 4.0 is not compatible with unpermitted commercial use. Seek separate terms or alternative permissible feeds.

## Stage gates
1. Working reproducible prototype and unit tests.
2. Legally usable real-world dataset; event/region holdout; transparent baseline results.
3. Customer-specific bench test with measured downstream MagNav position benefit, not only nT reduction.
4. Paid feasibility or pilot contract with explicit deliverable, data handling and acceptance criteria.
5. Hardened edge/API package; safety/cybersecurity assurance appropriate to the application.

Target customer interviews and metrics are planning assumptions, not booked revenue.
