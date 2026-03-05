"""
Training script for the RandomForest baseline model.
"""

import os

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from . import utils


def train_random_forest():
    df = utils.load_data()
    X, y, feature_cols = utils.build_rf_dataset(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    print("RandomForest classification report:")
    print(classification_report(y_test, y_pred))

    utils.ensure_directories()
    model_path = os.path.join(utils.MODEL_DIR, "rf_model.pkl")
    meta_path = os.path.join(utils.MODEL_DIR, "rf_metadata.pkl")

    joblib.dump(rf, model_path)
    joblib.dump({"feature_columns": feature_cols}, meta_path)

    return model_path, meta_path


def main():
    train_random_forest()


if __name__ == "__main__":
    main()
