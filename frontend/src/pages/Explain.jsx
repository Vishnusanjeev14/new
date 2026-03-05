import React, { useState } from "react";
import { explainRandomForest } from "../api.js";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function Explain() {
  const [featureNames, setFeatureNames] = useState([]);
  const [shapValues, setShapValues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExplain = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await explainRandomForest();
      setFeatureNames(res.feature_names || []);
      setShapValues(res.shap_values || []);
    } catch (e) {
      setError("Failed to compute SHAP values. Ensure RF model is trained.");
    } finally {
      setLoading(false);
    }
  };

  const data =
    featureNames.length && shapValues.length
      ? featureNames.map((name, idx) => ({
          feature: name,
          importance: shapValues[idx] ?? 0
        }))
      : [];

  return (
    <div className="explain-layout">
      <section className="card">
        <h2>RandomForest Explainability</h2>
        <p className="text-muted">
          Global feature importance estimated from SHAP values on the baseline
          RandomForest model.
        </p>

        <div style={{ marginTop: 14, marginBottom: 10 }}>
          <button className="btn" onClick={handleExplain} disabled={loading}>
            {loading ? "Computing SHAP..." : "Compute SHAP importances"}
          </button>
        </div>

        {error && (
          <div style={{ color: "#b91c1c", fontSize: "0.9rem" }}>{error}</div>
        )}

        {data.length > 0 && (
          <div style={{ marginTop: 14 }}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 8, right: 24, left: 32, bottom: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" />
                <YAxis dataKey="feature" type="category" width={80} />
                <Tooltip />
                <Bar
                  dataKey="importance"
                  fill="#22c55e"
                  radius={[0, 6, 6, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      <section className="card">
        <h2>Interpretation Guide</h2>
        <ul style={{ paddingLeft: 18, fontSize: "0.9rem", color: "#4b5563" }}>
          <li>
            <strong>MMSE</strong> – Cognitive score; lower values typically
            indicate worse impairment.
          </li>
          <li>
            <strong>ADAS13</strong> – Higher scores are commonly associated with
            worse cognitive status.
          </li>
          <li>
            <strong>Hippocampus</strong> – Volume; lower volume can reflect
            neurodegeneration.
          </li>
          <li>
            <strong>feature1 / feature2</strong> – Synthetic biomarkers used in
            this demo dataset.
          </li>
          <li>
            Bar length reflects mean absolute SHAP importance across patients
            and classes.
          </li>
        </ul>
      </section>
    </div>
  );
}

export default Explain;

