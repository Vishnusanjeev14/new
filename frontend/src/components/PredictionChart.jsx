import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function PredictionChart({ probabilities }) {
  if (!probabilities) {
    return (
      <p className="text-muted" style={{ marginTop: 4 }}>
        No prediction yet. Run a prediction to view probabilities.
      </p>
    );
  }

  const data = [
    { label: "CN", value: probabilities.cn ?? 0 },
    { label: "MCI", value: probabilities.mci ?? 0 },
    { label: "AD", value: probabilities.ad ?? 0 }
  ];

  const pct = (v) => `${(v * 100).toFixed(1)}%`;

  return (
    <div>
      <h3 style={{ marginBottom: 4 }}>Class Probabilities</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="label" />
          <YAxis tickFormatter={pct} domain={[0, 1]} />
          <Tooltip formatter={(v) => pct(v)} />
          <Bar dataKey="value" fill="#4f46e5" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PredictionChart;

