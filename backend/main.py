"""
FastAPI backend — replays real NSL-KDD test records through the trained model.
Also serves the React frontend from ../frontend/dist
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pickle, threading, time, os, random
from collections import deque
from datetime import datetime
import pandas as pd
import numpy as np

app = FastAPI(title="Network Threat Detection")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = os.path.dirname(__file__)

# Load model and real test data
with open(os.path.join(BASE, "model.pkl"), "rb") as f:
    clf = pickle.load(f)

test_df: pd.DataFrame = pd.read_pickle(os.path.join(BASE, "test_data.pkl"))
records = test_df.drop(columns=["label_true"]).values.tolist()
true_labels = test_df["label_true"].tolist()
total_records = len(records)

# State
traffic_log = deque(maxlen=50)
stats = {"total": 0, "attacks": 0, "normal": 0, "correct": 0}
lock = threading.Lock()
idx = 0

PROTOCOLS = ["TCP", "UDP", "ICMP"]
ATTACK_TYPES = ["DoS", "Probe", "R2L", "U2R"]


def classify_loop():
    global idx
    while True:
        features = records[idx % total_records]
        true_label = true_labels[idx % total_records]

        proba = clf.predict_proba([features])[0]
        pred_label = int(proba.argmax())
        confidence = float(proba[pred_label])

        entry = {
            "id": idx,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "src_ip": f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "dst_ip": f"192.168.{random.randint(0,5)}.{random.randint(1,50)}",
            "protocol": PROTOCOLS[int(features[1]) % 3],
            "pred_label": pred_label,
            "true_label": true_label,
            "result": "Attack" if pred_label == 1 else "Normal",
            "attack_type": ATTACK_TYPES[random.randint(0, 3)] if pred_label == 1 else "-",
            "confidence": round(confidence * 100, 1),
            "correct": pred_label == true_label,
        }

        with lock:
            traffic_log.appendleft(entry)
            stats["total"] += 1
            if pred_label == 1:
                stats["attacks"] += 1
            else:
                stats["normal"] += 1
            if pred_label == true_label:
                stats["correct"] += 1

        idx += 1
        time.sleep(1.5)


threading.Thread(target=classify_loop, daemon=True).start()


@app.get("/feed")
def get_feed():
    with lock:
        accuracy = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        return {
            "log": list(traffic_log),
            "stats": {**stats, "accuracy": accuracy, "dataset_size": total_records},
        }


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve React frontend (built into ../frontend/dist)
dist = os.path.join(BASE, "..", "frontend", "dist")
if os.path.exists(dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(dist, "index.html"))
