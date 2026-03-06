"""
Training script for the LSTM + attention sequence model.
"""

import os

import joblib
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from . import utils
from .models.lstm_attention import LSTMAttention


class SequenceDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def train_lstm(
    seq_len: int = 6,
    hidden_dim: int = 64,
    num_epochs: int = 20,
    batch_size: int = 32,
    lr: float = 1e-3,
):
    df = utils.load_data()
    X, y, rids, visit_months_list = utils.build_lstm_sequences(df, seq_len=seq_len)

    num_patients, seq_len_, num_features = X.shape
    X_reshaped = X.reshape(-1, num_features)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_reshaped)
    X_scaled = X_scaled.reshape(num_patients, seq_len_, num_features)

    X_train, X_val, y_train, y_val = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    train_ds = SequenceDataset(X_train, y_train)
    val_ds = SequenceDataset(X_val, y_val)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = LSTMAttention(
        input_dim=num_features, hidden_dim=hidden_dim, num_classes=3
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(1, num_epochs + 1):
        model.train()
        train_loss = 0.0
        for batch_X, batch_y in train_loader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            logits, _ = model(batch_X)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * batch_X.size(0)

        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X = batch_X.to(device)
                batch_y = batch_y.to(device)

                logits, _ = model(batch_X)
                loss = criterion(logits, batch_y)
                val_loss += loss.item() * batch_X.size(0)

                preds = torch.argmax(logits, dim=1)
                correct += (preds == batch_y).sum().item()
                total += batch_y.size(0)

        val_loss /= len(val_loader.dataset)
        val_acc = correct / total if total > 0 else 0.0
        print(
            f"Epoch {epoch}/{num_epochs} - "
            f"Train loss: {train_loss:.4f} - Val loss: {val_loss:.4f} - Val acc: {val_acc:.4f}"
        )

    utils.ensure_directories()
    model_path = os.path.join(utils.MODEL_DIR, "lstm_model.pt")
    scaler_path = os.path.join(utils.MODEL_DIR, "lstm_scaler.pkl")

    torch.save(model.state_dict(), model_path)
    joblib.dump(
        {
            "scaler": scaler,
            "seq_len": seq_len,
            "feature_columns": utils.FEATURE_COLUMNS,
        },
        scaler_path,
    )

    return model_path, scaler_path


def main():
    train_lstm()


if __name__ == "__main__":
    main()
