from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class GradientReversal(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor, lambda_: float) -> torch.Tensor:
        ctx.lambda_ = lambda_
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor) -> tuple[torch.Tensor, None]:
        return -ctx.lambda_ * grad_output, None


class FairnessAdversaryNet(nn.Module):
    """Predicts allocation outcome while hiding protected-group signal."""

    def __init__(self, input_dim: int, protected_classes: int, hidden_dim: int = 64) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.predictor = nn.Linear(hidden_dim, 1)
        self.adversary = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, protected_classes),
        )

    def forward(self, x: torch.Tensor, lambda_: float = 1.0) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x)
        outcome = self.predictor(z).squeeze(-1)
        reversed_z = GradientReversal.apply(z, lambda_)
        protected_logits = self.adversary(reversed_z)
        return outcome, protected_logits


def train_adversarial_model(
    x: torch.Tensor,
    y: torch.Tensor,
    protected: torch.Tensor,
    protected_classes: int,
    epochs: int = 25,
    lambda_: float = 0.7,
    batch_size: int = 64,
) -> FairnessAdversaryNet:
    model = FairnessAdversaryNet(input_dim=x.shape[1], protected_classes=protected_classes)
    loader = DataLoader(TensorDataset(x.float(), y.float(), protected.long()), batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    outcome_loss = nn.BCEWithLogitsLoss()
    protected_loss = nn.CrossEntropyLoss()

    model.train()
    for _ in range(epochs):
        for batch_x, batch_y, batch_protected in loader:
            optimizer.zero_grad()
            outcome_logits, protected_logits = model(batch_x, lambda_)
            loss = outcome_loss(outcome_logits, batch_y) + protected_loss(protected_logits, batch_protected)
            loss.backward()
            optimizer.step()

    return model
