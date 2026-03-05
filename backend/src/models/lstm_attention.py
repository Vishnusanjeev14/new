import torch
import torch.nn as nn
import torch.nn.functional as F


class LSTMAttention(nn.Module):
    """
    Minimal LSTM + attention skeleton.
    Will later be configured with concrete input dimensions and training logic.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 64, num_classes: int = 3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            batch_first=True,
        )
        self.attn = nn.Linear(hidden_dim, 1)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        """
        x: (batch, seq_len, input_dim)
        returns:
            logits: (batch, num_classes)
            attn_weights: (batch, seq_len)
        """
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden)
        scores = self.attn(lstm_out).squeeze(-1)  # (batch, seq_len)
        weights = F.softmax(scores, dim=1)
        context = (lstm_out * weights.unsqueeze(-1)).sum(dim=1)
        logits = self.fc(context)
        return logits, weights


__all__ = ["LSTMAttention"]

