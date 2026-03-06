import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/api",
  timeout: 15000
});

export async function healthCheck() {
  const res = await api.get("/health");
  return res.data;
}

export async function fetchPatients() {
  const res = await api.get("/patients");
  return res.data;
}

export async function fetchPatientVisits(rid) {
  const res = await api.get(`/patient/${rid}/visits`);
  return res.data;
}

export async function trainAllModels() {
  const res = await api.post("/train_all", {});
  return res.data;
}

export async function predictSingle(rid) {
  const res = await api.post("/predict", { mode: "single", rid });
  return res.data;
}

export async function predictSequence(rid) {
  const res = await api.post("/predict", { mode: "sequence", rid });
  return res.data;
}

export async function explainRandomForest() {
  const res = await api.post("/explain_rf", {});
  return res.data;
}

export default api;