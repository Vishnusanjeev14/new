import React from "react";

function AttentionHeatmap({ attention, visitMonths }) {
  if (!attention || attention.length === 0) return null;

  // 1. Find the extremes
  const max = Math.max(...attention);
  const min = Math.min(...attention);
  
  // 2. Calculate the "Stretch Factor"
  // If weights are 0.25 and 0.26, range is 0.01. 
  const range = max - min || 0.0001; 

  return (
    <div style={{ marginTop: "24px" }}>
      <h3>LSTM Temporal Attention</h3>
      <div className="heatmap-bars">
        {attention.map((w, idx) => {
          // 3. AMPLIFY THE DIFFERENCE
          // This formula makes the lowest weight 10% height 
          // and the highest weight 100% height.
          const amplifiedHeight = ((w - min) / range) * 90 + 10;
          
          return (
            <div key={idx} style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", justifyContent: "flex-end" }}>
              <div
                className="heatmap-bar"
                style={{ 
                  height: `${amplifiedHeight}%`,
                  // Also fade out less important bars
                  opacity: 0.3 + ((w - min) / range) * 0.7,
                  transition: "height 0.6s cubic-bezier(0.4, 0, 0.2, 1)" 
                }}
                title={`Raw Weight: ${w.toFixed(4)}`}
              />
              <div className="heatmap-label">{visitMonths[idx]}m</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AttentionHeatmap;