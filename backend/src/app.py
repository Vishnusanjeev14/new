from flask import Flask, jsonify, request
from flask_cors import CORS

from . import utils  # Added the dot here
from .train_rf import train_random_forest
from .train_lstm import train_lstm
from . import inference


def create_app():
    """
    Flask application with ML endpoints for the digital twin prototype.
    """
    app = Flask(__name__)
    CORS(app)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/api/patients", methods=["GET"])
    def get_patients():
        try:
            df = utils.load_data()
            patient_ids = utils.get_patient_ids(df)
            return jsonify({"patients": patient_ids})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/patient/<int:rid>/visits", methods=["GET"])
    def get_patient_visits(rid: int):
        try:
            df = utils.load_data()
            sub = utils.get_patient_visits(rid, df)
            if sub.empty:
                return jsonify({"error": f"No data found for RID={rid}"}), 404

            visits = []
            for _, row in sub.iterrows():
                visits.append(
                    {
                        "visit_month": int(row["visit_month"]),
                        "diag_label": int(row["diag_label"]),
                        "MMSE": float(row["MMSE"]),
                        "ADAS13": float(row["ADAS13"]),
                        "hippocampus": float(row["hippocampus"]),
                        "feature1": float(row["feature1"]),
                        "feature2": float(row["feature2"]),
                    }
                )

            return jsonify({"rid": rid, "visits": visits})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/train_all", methods=["POST"])
    def train_all():
        try:
            rf_model_path, _ = train_random_forest()
            lstm_model_path, _ = train_lstm()
            return jsonify(
                {
                    "message": "Training completed",
                    "rf_model_path": rf_model_path,
                    "lstm_model_path": lstm_model_path,
                }
            )
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/predict", methods=["POST"])
    def predict():
        payload = request.get_json(force=True) or {}
        mode = payload.get("mode")
        rid = payload.get("rid")

        if mode not in {"single", "sequence"}:
            return jsonify({"error": "mode must be 'single' or 'sequence'"}), 400
        if rid is None:
            return jsonify({"error": "rid is required"}), 400

        try:
            rid_int = int(rid)
        except (TypeError, ValueError):
            return jsonify({"error": "rid must be an integer"}), 400

        try:
            if mode == "single":
                pred_class, prob_map = inference.predict_rf_single(rid_int)
                return jsonify(
                    {
                        "mode": "single",
                        "rid": rid_int,
                        "predicted_class": pred_class,
                        "probabilities": prob_map,
                    }
                )

            pred_class, prob_map, attn, months = inference.predict_lstm_sequence(
                rid_int
            )
            return jsonify(
                {
                    "mode": "sequence",
                    "rid": rid_int,
                    "predicted_class": pred_class,
                    "probabilities": prob_map,
                    "attention": attn,
                    "visit_months": months,
                }
            )
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/explain_rf", methods=["POST"])
    def explain_rf():
        try:
            feature_names, shap_values = inference.explain_rf_global()
            return jsonify(
                {
                    "feature_names": feature_names,
                    "shap_values": shap_values,
                }
            )
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
