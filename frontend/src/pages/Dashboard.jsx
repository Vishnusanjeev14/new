import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchPatients, trainAllModels } from "../api.js";
import PatientCard from "../components/PatientCard.jsx";

function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchPatients();
        setPatients(data.patients || []);
      } catch (e) {
        setError("Failed to load patients. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleOpenTwin = (rid) => {
    navigate("/twin", { state: { rid } });
  };

  const handleTrain = async () => {
    setTraining(true);
    setError(null);
    try {
      await trainAllModels();
      alert("Training completed successfully.");
    } catch (e) {
      setError("Training failed. Check backend logs for details.");
    } finally {
      setTraining(false);
    }
  };

  return (
    <div>
      <div className="dashboard-header">
        <div>
          <h2>Patient Dashboard</h2>
          <div className="text-muted">
            View synthetic patients and open individual digital twins.
          </div>
        </div>
        <div className="dashboard-actions">
          <button className="btn" onClick={handleTrain} disabled={training}>
            {training ? (
              <>
                <span className="spinner" style={{ marginRight: 8 }} /> Training...
              </>
            ) : (
              "Train Models"
            )}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ color: "#b91c1c", marginBottom: 10, fontSize: "0.9rem" }}>
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-muted">Loading patients...</div>
      ) : patients.length === 0 ? (
        <div className="text-muted">No patients found in the dataset.</div>
      ) : (
        <div className="dashboard-grid">
          {patients.map((rid) => (
            <PatientCard key={rid} rid={rid} onOpen={handleOpenTwin} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;