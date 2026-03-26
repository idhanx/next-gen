# Next-Gen Network Threat Detection

An AI-powered network traffic monitoring system that classifies real network intrusion data in real time using a Random Forest model trained on the NSL-KDD dataset.

## Live Demo

> Frontend: `https://ngtd-frontend.onrender.com`
> Backend API: `https://ngtd-backend.onrender.com`

---

## What It Does

- Streams 22,544 real labeled NSL-KDD network records through a trained ML model
- Classifies each record as **Normal** or **Attack** (DoS, Probe, R2L, U2R)
- Shows live stats: total analyzed, attack rate, model accuracy
- Updates every 1.5 seconds automatically — no manual input needed

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, scikit-learn |
| ML Model | Random Forest (NSL-KDD dataset) |
| Frontend | React 18, TypeScript, Vite |
| Deploy | Render (2 services) |

---

## Project Structure

```
next-gen/
├── backend/
│   ├── main.py            # FastAPI app + background classifier loop
│   ├── train_nslkdd.py    # Downloads NSL-KDD + trains model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx        # Live dashboard UI
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── render.yaml            # Render deploy config
└── README.md
```

---

## Run Locally

**Backend**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_nslkdd.py      # downloads data + trains model (~30s)
uvicorn main:app --reload
```

**Frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## Deploy on Render

### Step 1 — Push to GitHub
```bash
git add .
git commit -m "initial commit"
git push origin main
```

### Step 2 — Create services on Render

Go to [render.com](https://render.com) → **New** → **Blueprint** → connect your GitHub repo.

Render will read `render.yaml` and create two services automatically:

| Service | Type | What it does |
|---------|------|-------------|
| `ngtd-backend` | Web Service (Python) | Trains model + runs FastAPI |
| `ngtd-frontend` | Web Service (Node) | Builds + serves React app |

### Step 3 — Set environment variable

After both services are created, go to `ngtd-frontend` → **Environment** → add:

```
VITE_API_URL = https://ngtd-backend.onrender.com
```

Then trigger a manual redeploy of the frontend.

---

## API

`GET /feed` — returns live classification results
```json
{
  "log": [
    {
      "timestamp": "14:32:01",
      "src_ip": "192.168.1.45",
      "dst_ip": "192.168.0.12",
      "protocol": "TCP",
      "result": "Attack",
      "attack_type": "DoS",
      "confidence": 94.2,
      "correct": true
    }
  ],
  "stats": {
    "total": 120,
    "attacks": 68,
    "normal": 52,
    "accuracy": 77.5,
    "dataset_size": 22544
  }
}
```

`GET /health` — health check
```json
{ "status": "ok" }
```

---

## Model Performance

Trained on NSL-KDD (125,973 training records), evaluated on 22,544 test records:

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Normal | 0.66 | 0.97 | 0.78 |
| Attack | 0.97 | 0.62 | 0.75 |
| **Overall accuracy** | | | **77%** |
