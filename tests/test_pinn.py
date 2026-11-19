import pytest

torch = pytest.importorskip("torch")
from spacetech.pinn import curl_from_potential, CurlFieldPINN, fit_field


class PolynomialPotential(torch.nn.Module):
    def forward(self, x):
        # A_z = x*y -> B=(x,-y,0), whose divergence is exactly 0.
        return torch.stack((x[:, 0] * 0, x[:, 0] * 0, x[:, 0] * x[:, 1]), dim=1)


def test_curl_enforces_divergence_free_field():
    coords = torch.tensor([[0.4, -0.3, 0.1, 0.7], [0.2, 0.1, -0.5, 0.2]])
    coords.requires_grad_(True)
    b = curl_from_potential(PolynomialPotential(), coords)
    expected = torch.stack((coords[:, 0], -coords[:, 1], torch.zeros(2)), dim=1)
    torch.testing.assert_close(b, expected)
    grad_bx = torch.autograd.grad(b[:, 0].sum(), coords, retain_graph=True)[0][:, 0]
    grad_by = torch.autograd.grad(b[:, 1].sum(), coords)[0][:, 1]
    torch.testing.assert_close(grad_bx + grad_by, torch.zeros(2))


def test_pinn_training_path_runs():
    torch.manual_seed(1)
    coords = torch.rand(16, 4) * 2 - 1
    truth = torch.stack((coords[:, 0], -coords[:, 1], torch.zeros(16)), dim=1)
    model = CurlFieldPINN(width=12)
    losses = fit_field(model, coords, truth, epochs=15, lr=0.01)
    assert len(losses) == 15
    assert losses[-1] < losses[0]
