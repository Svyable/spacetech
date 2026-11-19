import numpy as np
import pytest

from spacetech.forecast import (
    CausalDisturbanceFilter, FieldForecast, benchmark_forecasts,
    correct_magnetometer, generate_synthetic_disturbance,
)


def test_filter_is_causal_and_rejects_gross_spike():
    f = CausalDisturbanceFilter(observation_sigma_nT=1, initial_sigma_nT=2)
    for _ in range(25):
        assert f.update([1, -3, 5])
    before = f.forecast(5)
    assert f.update([10000, -3, 5]) is False
    assert f.rejected == 1
    after = f.forecast(4)
    # The outlier does not become a false 10,000 nT disturbance estimate.
    assert abs(after.mean_nT[0] - before.mean_nT[0]) < 1


def test_forecast_uncertainty_increases_with_lead():
    f = CausalDisturbanceFilter()
    for _ in range(30):
        f.update([0, 0, 0])
    near, far = f.forecast(1), f.forecast(15)
    assert np.all(far.sigma_nT > near.sigma_nT)
    assert far.observations_accepted == 30


def test_missing_sample_preserves_time_axis():
    a, b = CausalDisturbanceFilter(), CausalDisturbanceFilter()
    a.update([0, 0, 0])
    b.update([0, 0, 0])
    a.update([np.nan, np.nan, np.nan])
    b.update(None)
    np.testing.assert_allclose(a.forecast(1).mean_nT, b.forecast(1).mean_nT)
    assert a.missing == b.missing == 1


def test_correction_refuses_uncertain_prediction():
    low = FieldForecast(np.array([7., -2., 1.]), np.array([1., 1., 1.]), 5, 20)
    np.testing.assert_allclose(correct_magnetometer([100., 80., 70.], low),
                               [93., 82., 69.])
    high = FieldForecast(np.zeros(3), np.ones(3) * 51, 5, 20)
    with pytest.raises(ValueError, match="uncertainty"):
        correct_magnetometer([1, 2, 3], high)


def test_hindcast_metrics_are_reproducible_and_labeled():
    observations, latent_truth = generate_synthetic_disturbance(count=400, seed=2)
    a = benchmark_forecasts(observations, 5, 30, latent_truth)
    b = benchmark_forecasts(observations, 5, 30, latent_truth)
    assert a == b
    assert a["evaluated_origins"] > 250
    assert a["target_kind"] == "synthetic_latent_truth"
    assert a["filter"]["rmse_vector_nT"] >= 0
    assert a["persistence"]["rmse_vector_nT"] >= 0


def test_requires_valid_shape_and_horizon():
    with pytest.raises(ValueError, match="N x 3"):
        benchmark_forecasts(np.ones((10, 2)))
    with pytest.raises(ValueError, match="positive"):
        benchmark_forecasts(np.ones((10, 3)), horizon_steps=0)
    with pytest.raises(ValueError, match="three-component"):
        CausalDisturbanceFilter().update([1, 2])
