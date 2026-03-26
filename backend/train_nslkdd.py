"""
Download NSL-KDD dataset and train a Random Forest classifier.
Saves model.pkl for use by main.py.
"""
import os
import pickle
import urllib.request
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# NSL-KDD column names (41 features + label + difficulty)
COLUMNS = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes",
    "land","wrong_fragment","urgent","hot","num_failed_logins","logged_in",
    "num_compromised","root_shell","su_attempted","num_root","num_file_creations",
    "num_shells","num_access_files","num_outbound_cmds","is_host_login",
    "is_guest_login","count","srv_count","serror_rate","srv_serror_rate",
    "rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate",
    "srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","label","difficulty"
]

TRAIN_URL = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain+.txt"
TEST_URL  = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest+.txt"

DATA_DIR = os.path.dirname(__file__)
TRAIN_PATH = os.path.join(DATA_DIR, "KDDTrain+.txt")
TEST_PATH  = os.path.join(DATA_DIR, "KDDTest+.txt")
MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
ENCODER_PATH = os.path.join(DATA_DIR, "encoders.pkl")
DATA_CACHE = os.path.join(DATA_DIR, "test_data.pkl")


def download(url, path):
    if not os.path.exists(path):
        print(f"Downloading {url} ...")
        urllib.request.urlretrieve(url, path)
        print(f"Saved to {path}")
    else:
        print(f"Already exists: {path}")


def load_df(path):
    df = pd.read_csv(path, header=None, names=COLUMNS)
    df.drop(columns=["difficulty"], inplace=True)
    # Binary label: normal=0, anything else=1
    df["label"] = (df["label"].str.strip().str.lower() != "normal").astype(int)
    return df


def encode_and_fit(df, encoders=None):
    cat_cols = ["protocol_type", "service", "flag"]
    if encoders is None:
        encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
    else:
        for col in cat_cols:
            le = encoders[col]
            df[col] = df[col].astype(str).map(
                lambda x, le=le: le.transform([x])[0] if x in le.classes_ else 0
            )
    return df, encoders


def train():
    download(TRAIN_URL, TRAIN_PATH)
    download(TEST_URL, TEST_PATH)

    print("Loading training data...")
    train_df = load_df(TRAIN_PATH)
    train_df, encoders = encode_and_fit(train_df)

    print("Loading test data...")
    test_df = load_df(TEST_PATH)
    test_df, _ = encode_and_fit(test_df, encoders)

    feature_cols = [c for c in COLUMNS if c not in ("label", "difficulty")]
    X_train = train_df[feature_cols].values
    y_train = train_df["label"].values
    X_test  = test_df[feature_cols].values
    y_test  = test_df["label"].values

    print("Training Random Forest...")
    clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    clf.fit(X_train, y_train)

    print("\nTest set performance:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["Normal", "Attack"]))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoders, f)

    # Cache test rows for live replay
    test_df["label_true"] = y_test
    test_df[feature_cols + ["label_true"]].to_pickle(DATA_CACHE)

    print(f"\nModel saved: {MODEL_PATH}")
    print(f"Test data cached: {DATA_CACHE} ({len(test_df)} rows)")


if __name__ == "__main__":
    train()
