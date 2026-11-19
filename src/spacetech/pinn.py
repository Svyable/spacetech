"""Optional research PINN building block: vector potential implies div(B)=0.

This is a *spatially constrained neural field*, NOT a validated short-term
forecast. Coordinates are normalized (x,y,z,t), with a common length scale
for x/y/z so the curl is physically consistent up to a common conversion.
The time coordinate does not enter Maxwell's divergence condition.
Requires the optional torch extra.
"""
import torch
from torch import nn


def curl_from_potential(potential, coords):
    """Differentiable curl(A) with create_graph for neural training."""
    if coords.ndim != 2 or coords.shape[1] != 4:
        raise ValueError("coords must be N x 4 normalized [x,y,z,t]")
    with torch.enable_grad():
        x = coords.clone().requires_grad_(True)
        a = potential(x)
        if a.shape != (x.shape[0], 3):
            raise ValueError("vector potential must return N x 3")
        derivs = [
            torch.autograd.grad(a[:, i].sum(), x, retain_graph=True, create_graph=True)[0]
            for i in range(3)
        ]
        b = torch.stack((
            derivs[2][:, 1] - derivs[1][:, 2],
            derivs[0][:, 2] - derivs[2][:, 0],
            derivs[1][:, 0] - derivs[0][:, 1],
        ), dim=1)
    return b


class CurlFieldPINN(nn.Module):
    def __init__(self, width=48):
        super().__init__()
        self.potential = nn.Sequential(
            nn.Linear(4, width), nn.Tanh(),
            nn.Linear(width, width), nn.Tanh(),
            nn.Linear(width, 3),
        )

    def forward(self, coords):
        return curl_from_potential(self.potential, coords)


def fit_field(model, coords, field_nT, epochs=100, lr=0.001):
    """Fit known vector samples; no leakage-safe forecast evaluation implied."""
    if coords.ndim != 2 or coords.shape[1] != 4:
        raise ValueError("coords must be N x 4")
    if field_nT.shape != (coords.shape[0], 3):
        raise ValueError("field_nT must be N x 3")
    if epochs < 1 or lr <= 0:
        raise ValueError("epochs and lr must be positive")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    losses = []
    for _ in range(epochs):
        optimizer.zero_grad()
        field = model(coords)
        loss = ((field - field_nT) ** 2).mean()
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    return losses
