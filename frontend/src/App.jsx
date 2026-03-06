import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
// Ensure these paths correctly point to the 'pages' subfolder relative to App.jsx
import Dashboard from "./pages/Dashboard.jsx";
import PatientTwin from "./pages/PatientTwin.jsx";
import Explain from "./pages/Explain.jsx";



function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-gradient" />
        <div className="header-content">
          <h1>Alzheimer's Digital Twin</h1>
          <nav className="nav-links">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/twin"
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              Patient Twin
            </NavLink>
            <NavLink
              to="/explain"
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              Explainability
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/twin" element={<PatientTwin />} />
          <Route path="/explain" element={<Explain />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;