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

  // Load the full patient list for the dropdown
  useEffect(() => {
    async function loadPatients() {
      try {
        const data = await fetchPatients();
        setPatients(data.patients || []);
        if (!initialRid && data.patients?.length > 0) {
          setSelectedRid(data.patients[0]);
        }
      } catch (e) {
        setError("Failed to load patient list.");
      }
    }
    loadPatients();
  }, [initialRid]);

  // Load visit history when a patient is selected
  useEffect(() => {
    if (!selectedRid) return;
    async function loadVisits() {
      setLoadingVisits(true);
      try {
        const data = await fetchPatientVisits(selectedRid);
        setVisits(data.visits || []);
      } catch (e) {
        setError("Could not retrieve patient visits.");
      } finally {
        setLoadingVisits(false);
      }
    }
    loadVisits();
  }, [selectedRid]);

  const handlePredictLstm = async () => {
    setLoadingPredict(true);
    try {
      const res = await predictSequence(selectedRid); //
      setProbabilities(res.probabilities);
      setAttention(res.attention);
      setVisitMonths(res.visit_months);
    } catch (e) {
      setError("LSTM prediction failed. Ensure models are trained.");
    } finally {
      setLoadingPredict(false);
    }
  };

  return (
    <div className="twin-layout">
      <section className="card twin-panel">
        <h2>Patient Digital Twin: #{selectedRid}</h2>
        <div className="timeline">
          {visits.map((v, i) => (
            <div key={i} className="timeline-row">
              <strong>Month {v.visit_month}:</strong> Dx {v.diag_label} (MMSE: {v.MMSE})
            </div>
          ))}
        </div>
        <button className="btn" onClick={handlePredictLstm} disabled={loadingPredict}>
          {loadingPredict ? "Processing..." : "Run LSTM Digital Twin"}
        </button>
      </section>

      <section className="card twin-panel">
        <PredictionChart probabilities={probabilities} />
        <AttentionHeatmap attention={attention} visitMonths={visitMonths} />
      </section>
    </div>
  );
}

export default PatientTwin;