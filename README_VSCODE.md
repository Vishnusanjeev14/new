# Running the Digital Twin Project in VS Code (Step by Step on Windows)

This guide walks you through running the **backend (Flask)** and **frontend (React + Vite)** in **VS Code**, starting from an empty workspace.

> Assumptions:
> - You are on Windows.
> - You have **Python 3.9+**, **Node.js 18+**, and **Git** installed.
> - You are opening the folder `c:\Users\Vishnu\Desktop\pred2` in VS Code.

---

## 1. Open the Project in VS Code

1. Start **VS Code**.
2. Click **File → Open Folder...**.
3. Select `c:\Users\Vishnu\Desktop\pred2` and click **Select Folder**.
4. You should see two main folders in the Explorer:
   - `backend`
   - `frontend`

---

## 2. Set Up and Run the Backend (Flask API)

### 2.1 Open a backend terminal

1. In VS Code, open the integrated terminal:
   - Menu: **Terminal → New Terminal**
2. In the terminal, change directory to the backend:

```powershell
cd backend
```

You should now be in `c:\Users\Vishnu\Desktop\pred2\backend`.

### 2.2 Create and activate a virtual environment

Create a virtual environment named `venv`:

```powershell
python -m venv venv
```

Activate it (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt.

> If PowerShell blocks script execution, you may need to run VS Code as Administrator once and use:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2.3 Install backend dependencies

With the venv activated and still in the `backend` directory:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Run the Flask backend

Still in the same terminal:

```powershell
python src/app.py
```

You should see Flask logs and something like:

```text
Running on http://127.0.0.1:5000
```

Leave this terminal **running**; this is your backend API server.

> Quick check: Open a browser and go to  
> `http://127.0.0.1:5000/api/health`  
> You should see: `{"status": "ok"}`.

---

## 3. Set Up and Run the Frontend (React + Vite)

### 3.1 Open a second terminal for the frontend

1. In VS Code, open **another** integrated terminal:
   - Menu: **Terminal → New Terminal**
2. Change directory to the frontend:

```powershell
cd frontend
```

You should now be in `c:\Users\Vishnu\Desktop\pred2\frontend`.

### 3.2 Install frontend dependencies

Run:

```powershell
npm install
```

This installs React, Vite, Axios, Recharts, and React Router.

### 3.3 Start the Vite dev server

Still in the `frontend` directory:

```powershell
npm run dev
```

Vite will start and print a URL like:

```text
Local:   http://127.0.0.1:5173/
```

Hold **Ctrl + Click** on that URL in the terminal (or copy/paste it into your browser) to open the frontend.

---

## 4. Typical VS Code Workflow

1. **Start VS Code** and open the `pred2` folder.
2. **Terminal 1 (backend)**
   - `cd backend`
   - `.\venv\Scripts\Activate.ps1`
   - `python src/app.py`
3. **Terminal 2 (frontend)**
   - `cd frontend`
   - `npm install` (first time only)
   - `npm run dev`
4. Keep both terminals running while you:
   - Edit backend files under `backend/src/` (e.g., `app.py`).
   - Edit frontend files under `frontend/src/` (e.g., `App.jsx`, pages, components).
5. The **frontend reloads automatically** when you save React files.  
   If you change backend Python code, use **Ctrl + C** in the backend terminal and re-run `python src/app.py`.

---

## 5. Useful VS Code Tips for This Project

- **Python interpreter**
  - Press **Ctrl + Shift + P** → type **Python: Select Interpreter**.
  - Choose the interpreter from `backend\venv\Scripts\python.exe` so linting/IntelliSense uses your venv.

- **ESLint / Prettier (optional)**
  - If you install VS Code extensions for ESLint or Prettier, they will help format your React code.

- **Debugging backend**
  - You can add breakpoints in `backend/src/app.py`, then use the **Run and Debug** panel to start a Python debug configuration pointing to `src/app.py`.

- **Debugging frontend**
  - Use the **Microsoft Edge Tools** or **Chrome DevTools** to inspect the React app while Vite is running.

---

## 6. Stopping the Servers

To stop either server (backend or frontend):

1. Click into the corresponding VS Code terminal.
2. Press **Ctrl + C**.

You can restart them later with:

- Backend: `cd backend`, activate venv, `python src/app.py`
- Frontend: `cd frontend`, `npm run dev`

---

You now have a complete VS Code workflow to run and develop this project end-to-end on your local machine. 

