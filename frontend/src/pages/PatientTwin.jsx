import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import {
  fetchPatients,
  fetchPatientVisits,
  predictSequence,
  predictSingle
} from "../api.js";
import PredictionChart from "../components/PredictionChart.jsx";
import AttentionHeatmap from "../components/AttentionHeatmap.jsx";

function PatientTwin() {
  const location = useLocation();
  const initialRid = location.state?.rid;

  const [patients, setPatients] = useState([]);
  const [selectedRid, setSelectedRid] = useState(initialRid || "");
  const [visits, setVisits] = useState([]);
  const [probabilities, setProbabilities] = useState(null);
  const [attention, setAttention] = useState([]);
  const [visitMonths, setVisitMonths] = useState([]);
  const [loadingVisits, setLoadingVisits] = useState(false);
  const [loadingPredict, setLoadingPredict] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadPatients() {
      try {
        const data = await fetchPatients();
        setPatients(data.patients || []);
        if (!initialRid && data.patients && data.patients.length > 0) {
          setSelectedRid(data.patients[0]);
        }
      } catch (e) {
        setError("Failed to load patients. Check backend connection.");
      }
    }
    loadPatients();
  }, [initialRid]);

  useEffect(() => {
    if (!selectedRid) return;
    async function loadVisits() {
      setLoadingVisits(true);
      setError(null);
      try {
        const data = await fetchPatientVisits(selectedRid);
        setVisits(data.visits || []);
      } catch (e) {
        setError("Failed to load visits for patient.");
        setVisits([]);
      } finally {
        setLoadingVisits(false);
      }
    }
    loadVisits();
  }, [selectedRid]);

  const handlePredictLstm = async () => {
    if (!selectedRid) return;
    setLoadingPredict(true);
    setError(null);
    try {
      const res = await predictSequence(selectedRid);
      setProbabilities(res.probabilities || null);
      setAttention(res.attention || []);
      setVisitMonths(res.visit_months || []);
    } catch (e) {
      setError("LSTM prediction failed. Ensure models are trained.");
    } finally {
      setLoadingPredict(false);
    }
  };

  const handlePredictRf = async () => {
    if (!selectedRid) return;
    setLoadingPredict(true);
    setError(null);
    try {
      const res = await predictSingle(selectedRid);
      setProbabilities(res.probabilities || null);
      setAttention([]);
      setVisitMonths([]);
    } catch (e) {
      setError("RandomForest prediction failed. Ensure models are trained.");
    } finally {
      setLoadingPredict(false);
    }
  };

  const currentDiag =
    visits.length > 0 ? visits[visits.length - 1].diag_label : null;

  return (
    <div className="twin-layout">
      <section className="card twin-panel">
        <h2>Patient Digital Twin</h2>
        <p className="text-muted">
          Inspect longitudinal visits and run sequence-based predictions with
          attention.
        </p>

        <div className="select-row">
          <span style={{ fontSize: "0.9rem" }}>Select patient:</span>
          <select
            value={selectedRid || ""}
            onChange={(e) => setSelectedRid(Number(e.target.value))}
          >
            {patients.map((rid) => (
              <option key={rid} value={rid}>
                #{rid}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div style={{ color: "#b91c1c", marginBottom: 8, fontSize: "0.9rem" }}>
            {error}
          </div>
        )}

        <h3>Visit Timeline</h3>
        {loadingVisits ? (
          <div className="text-muted">Loading visits...</div>
        ) : visits.length === 0 ? (
          <div className="text-muted">
            No visits found for this synthetic patient.
          </div>
        ) : (
          <div className="timeline">
            {visits.map((v, idx) => (
              <div className="timeline-row" key={idx}>
                <span>
                  <strong>{v.visit_month} months</strong>
                </span>
                <span>
                  Dx: {v.diag_label === 0 ? "CN" : v.diag_label === 1 ? "MCI" : "AD"}
                </span>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: 14, display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            className="btn"
            onClick={handlePredictLstm}
            disabled={loadingPredict || !selectedRid}
          >
            {loadingPredict ? "Predicting..." : "Predict with LSTM (sequence)"}
          </button>
          <button
            className="btn btn-secondary"
            onClick={handlePredictRf}
            disabled={loadingPredict || !selectedRid}
          >
            Baseline RF (latest visit)
          </button>
        </div>

        {currentDiag !== null && (
          <div
            className="text-muted"
            style={{ marginTop: 10, fontSize: "0.85rem" }}
          >
            Latest recorded label for this synthetic patient:{" "}
            <strong>
              {currentDiag === 0 ? "Cognitively normal" : currentDiag === 1 ? "MCI" : "AD"}
            </strong>
          </div>
        )}
      </section>

      <section className="card twin-panel">
        <h2>Model Outputs</h2>
        <PredictionChart probabilities={probabilities} />
        <AttentionHeatmap attention={attention} visitMonths={visitMonths} />
      </section>
    </div>
  );
}

export default PatientTwin;

