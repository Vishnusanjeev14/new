import React from "react";

function AttentionHeatmap({ attention, visitMonths }) {
  if (!attention || !attention.length) {
    return (
      <p className="text-muted" style={{ marginTop: 4 }}>
        No attention weights yet. Run LSTM prediction to view temporal focus.
      </p>
    );
  }

  const max = Math.max(...attention, 0.0001);

  return (
    <div style={{ marginTop: 12 }}>
      <h3 style={{ marginBottom: 4 }}>Attention Over Time</h3>
      <div className="heatmap-bars">
        {attention.map((w, idx) => {
          const heightPct = (w / max) * 100;
          const month = visitMonths?.[idx];
          return (
            <div key={idx} style={{ flex: 1 }}>
              <div
                className="heatmap-bar"
                style={{ height: `${Math.max(heightPct, 8)}%` }}
                title={`Weight: ${w.toFixed(3)}${
                  month !== undefined ? `, Month: ${month}` : ""
                }`}
              />
              <div className="heatmap-label">
                {month !== undefined ? `${month}m` : `t${idx + 1}`}
              </div>
            </div>
          );
        })}
      </div>
      <div className="heatmap-legend">
        Higher bars indicate visits the LSTM+attention focused on more strongly.
      </div>
    </div>
  );
}

export default AttentionHeatmap;

