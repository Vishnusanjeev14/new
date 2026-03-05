import React from "react";

function PatientCard({ rid, onOpen }) {
  return (
    <div className="card">
      <h3>Patient #{rid}</h3>
      <p className="text-muted">Starter patient card component.</p>
      {onOpen && (
        <button className="btn" type="button" onClick={() => onOpen(rid)}>
          Open Twin
        </button>
      )}
    </div>
  );
}

export default PatientCard;

