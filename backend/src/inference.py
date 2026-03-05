"""
Inference utilities for the RandomForest and LSTM+attention models,
and SHAP-based explainability for the RandomForest baseline.
"""

import os
from typing import Tuple

import joblib
import numpy as np
import shap
import torch

from . import utils
from .models.lstm_attention import LSTMAttention


_rf_model = None
_rf_meta = None
_lstm_model = None
_lstm_meta = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_rf():
    global _rf_model, _rf_meta
    if _rf_model is not None:
        return _rf_model, _rf_meta

    model_path = os.path.join(utils.MODEL_DIR, "rf_model.pkl")
    meta_path = os.path.join(utils.MODEL_DIR, "rf_metadata.pkl")
    if not os.path.exists(model_path):
        raise RuntimeError("RandomForest model not found. Train it via /api/train_all.")

    _rf_model = joblib.load(model_path)
    _rf_meta = joblib.load(meta_path) if os.path.exists(meta_path) else {}
    return _rf_model, _rf_meta


def load_lstm():
    global _lstm_model, _lstm_meta
    if _lstm_model is not None:
        return _lstm_model, _lstm_meta

    model_path = os.path.join(utils.MODEL_DIR, "lstm_model.pt")
    scaler_path = os.path.join(utils.MODEL_DIR, "lstm_scaler.pkl")
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise RuntimeError("LSTM model or scaler not found. Train it via /api/train_all.")

    meta = joblib.load(scaler_path)
    scaler = meta["scaler"]
    seq_len = meta["seq_len"]
    feature_columns = meta["feature_columns"]

    input_dim = len(feature_columns)
    model = LSTMAttention(input_dim=input_dim, hidden_dim=64, num_classes=3)
    model.load_state_dict(torch.load(model_path, map_location=_device))
    model.to(_device)
    model.eval()

    _lstm_model = model
    _lstm_meta = {
        "scaler": scaler,
        "seq_len": seq_len,
        "feature_columns": feature_columns,
    }
    return _lstm_model, _lstm_meta


def predict_rf_single(rid: int) -> Tuple[int, dict]:
    df = utils.load_data()
    x = utils.get_latest_visit_features_for_rid(rid, df)
    if x is None:
        raise ValueError(f"No data found for RID={rid}")

    rf, meta = load_rf()
    _ = meta.get("feature_columns", utils.FEATURE_COLUMNS)

    x_arr = np.array([x], dtype=float)
    probs = rf.predict_proba(x_arr)[0]
    pred_class = int(np.argmax(probs))

    prob_map = {
        "cn": float(probs[0]),
        "mci": float(probs[1]),
        "ad": float(probs[2]),
    }

    return pred_class, prob_map


def predict_lstm_sequence(rid: int):
    df = utils.load_data()
    model, meta = load_lstm()
    scaler = meta["scaler"]
    seq_len = meta["seq_len"]
    feature_columns = meta["feature_columns"]

    seq_feats, months = utils.get_sequence_for_rid(rid, seq_len=seq_len, df=df)
    if seq_feats is None:
        raise ValueError(f"No data found for RID={rid}")

    num_features = len(feature_columns)
    seq_feats = seq_feats.reshape(-1, num_features)
    seq_scaled = scaler.transform(seq_feats)
    seq_scaled = seq_scaled.reshape(1, seq_len, num_features)

    x_tensor = torch.tensor(seq_scaled, dtype=torch.float32, device=_device)
    with torch.no_grad():
        logits, attn_weights = model(x_tensor)

    probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
    attn = attn_weights.cpu().numpy()[0]
    pred_class = int(np.argmax(probs))

    prob_map = {
        "cn": float(probs[0]),
        "mci": float(probs[1]),
        "ad": float(probs[2]),
    }

    return pred_class, prob_map, attn.tolist(), list(map(int, months.tolist()))


def explain_rf_global(max_samples: int = 200):
    df = utils.load_data()
    X, y, feature_cols = utils.build_rf_dataset(df)
    rf, meta = load_rf()
    feature_cols = meta.get("feature_columns", feature_cols)

    if X.shape[0] > max_samples:
        idx = np.random.choice(X.shape[0], size=max_samples, replace=False)
        X_sample = X[idx]
    else:
        X_sample = X

    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_sample)

    abs_means_per_class = [np.mean(np.abs(s), axis=0) for s in shap_values]
    global_shap = np.mean(np.stack(abs_means_per_class, axis=0), axis=0)

    return feature_cols, global_shap.tolist()
