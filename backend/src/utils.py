import os
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "adni_sample.csv")

MODEL_DIR = os.path.join(BASE_DIR, "models")

FEATURE_COLUMNS = ["MMSE", "ADAS13", "hippocampus", "feature1", "feature2"]


def ensure_directories() -> None:
    """
    Ensure core backend directories exist.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)


def generate_dummy_dataset(num_patients: int = 100, num_visits: int = 4) -> pd.DataFrame:
    """
    Generate a synthetic longitudinal dataset:
      - num_patients subjects
      - num_visits visits per subject
      - decreasing MMSE over time, increasing ADAS13, decreasing hippocampus
    """
    np.random.seed(42)
    rows = []
    visit_months = [0, 6, 12, 18][:num_visits]

    for i in range(num_patients):
        rid = 1001 + i
        base_mmse = np.random.randint(24, 30)
        base_adas = np.random.randint(8, 15)
        base_hippo = np.random.randint(3200, 3800)
        base_f1 = np.random.uniform(0.05, 0.2)
        base_f2 = np.random.uniform(0.9, 1.1)

        for v_idx, month in enumerate(visit_months):
            mmse = base_mmse - v_idx * np.random.uniform(0.5, 2.0)
            adas = base_adas + v_idx * np.random.uniform(0.5, 3.0)
            hippo = base_hippo - v_idx * np.random.uniform(20, 80)

            if v_idx == 0:
                diag = 0
            elif v_idx == 1:
                diag = np.random.choice([0, 1], p=[0.6, 0.4])
            elif v_idx == 2:
                diag = np.random.choice([1, 2], p=[0.6, 0.4])
            else:
                diag = np.random.choice([1, 2], p=[0.3, 0.7])

            feature1 = base_f1 + np.random.normal(0, 0.01)
            feature2 = base_f2 + np.random.normal(0, 0.02)

            rows.append(
                {
                    "RID": rid,
                    "visit_month": month,
                    "diag_label": int(diag),
                    "MMSE": float(np.round(mmse, 2)),
                    "ADAS13": float(np.round(adas, 2)),
                    "hippocampus": float(np.round(hippo, 2)),
                    "feature1": float(np.round(feature1, 3)),
                    "feature2": float(np.round(feature2, 3)),
                }
            )

    return pd.DataFrame(rows)


def ensure_dummy_data() -> None:
    """
    Ensure that the dataset exists and has data.
    If the file is missing or has too few rows, generate a dummy dataset.
    """
    ensure_directories()
    if not os.path.exists(DATA_PATH):
        df = generate_dummy_dataset()
        df.to_csv(DATA_PATH, index=False)
        return

    try:
        df = pd.read_csv(DATA_PATH)
    except Exception:
        df = generate_dummy_dataset()
        df.to_csv(DATA_PATH, index=False)
        return

    if df.shape[0] < 10:
        df = generate_dummy_dataset()
        df.to_csv(DATA_PATH, index=False)


def load_data() -> pd.DataFrame:
    ensure_dummy_data()
    return pd.read_csv(DATA_PATH)


def get_patient_ids(df=None):
    if df is None:
        df = load_data()
    return sorted(df["RID"].unique().tolist())


def get_patient_visits(rid: int, df=None):
    if df is None:
        df = load_data()
    sub = df[df["RID"] == rid].copy()
    return sub.sort_values("visit_month")


def build_rf_dataset(df: pd.DataFrame):
    X = df[FEATURE_COLUMNS].values
    y = df["diag_label"].astype(int).values
    return X, y, FEATURE_COLUMNS


def build_lstm_sequences(df: pd.DataFrame, seq_len: int = 6):
    """
    Build one fixed-length sequence per patient.
    If a patient has fewer than seq_len visits, pad by repeating the last visit.
    If more, use the most recent seq_len visits.
    """
    rids = get_patient_ids(df)
    X_list = []
    y_list = []
    visit_months_list = []

    for rid in rids:
        sub = get_patient_visits(rid, df)
        feats = sub[FEATURE_COLUMNS].values
        labels = sub["diag_label"].astype(int).values
        months = sub["visit_month"].values

        if len(feats) >= seq_len:
            feats_seq = feats[-seq_len:]
            months_seq = months[-seq_len:]
            label = labels[-1]
        else:
            pad_count = seq_len - len(feats)
            last_feat = feats[-1]
            last_month = months[-1]
            pad_feats = np.tile(last_feat, (pad_count, 1))
            pad_months = [last_month + 6 * (i + 1) for i in range(pad_count)]

            feats_seq = np.vstack([feats, pad_feats])
            months_seq = np.concatenate([months, np.array(pad_months)])
            label = labels[-1]

        X_list.append(feats_seq)
        y_list.append(label)
        visit_months_list.append(months_seq)

    X = np.stack(X_list, axis=0)
    y = np.array(y_list)
    return X, y, rids, visit_months_list


def get_latest_visit_features_for_rid(rid: int, df=None):
    if df is None:
        df = load_data()
    sub = get_patient_visits(rid, df)
    if sub.empty:
        return None
    latest = sub.iloc[-1]
    return latest[FEATURE_COLUMNS].values.astype(float)


def get_sequence_for_rid(
    rid: int, seq_len: int = 6, df= None
):
    if df is None:
        df = load_data()
    sub = get_patient_visits(rid, df)
    if sub.empty:
        return None, None

    feats = sub[FEATURE_COLUMNS].values
    months = sub["visit_month"].values

    if len(feats) >= seq_len:
        feats_seq = feats[-seq_len:]
        months_seq = months[-seq_len:]
    else:
        pad_count = seq_len - len(feats)
        last_feat = feats[-1]
        last_month = months[-1]
        pad_feats = np.tile(last_feat, (pad_count, 1))
        pad_months = [last_month + 6 * (i + 1) for i in range(pad_count)]
        feats_seq = np.vstack([feats, pad_feats])
        months_seq = np.concatenate([months, np.array(pad_months)])

    return feats_seq, months_seq


if __name__ == "__main__":
    # Regenerate dummy data if needed when run directly.
    ensure_dummy_data()
