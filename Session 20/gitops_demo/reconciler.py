import time
import os
import subprocess
import yaml
import json
from datetime import datetime

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "repo"))
CLUSTER_STATE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "cluster_live_state.json"))

def run_git(cmd):
    result = subprocess.run(f"git -C \"{REPO_PATH}\" {cmd}", shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_git_head_info():
    commit_hash = run_git("rev-parse --short HEAD")
    commit_msg = run_git("log -1 --pretty=%B")
    return commit_hash, commit_msg

def load_desired_state():
    manifest_path = os.path.join(REPO_PATH, "deployment.yaml")
    if not os.path.exists(manifest_path):
        return None
    with open(manifest_path, "r") as f:
        return yaml.safe_load(f)

def load_live_cluster_state():
    if not os.path.exists(CLUSTER_STATE_FILE):
        return {}
    with open(CLUSTER_STATE_FILE, "r") as f:
        return json.load(f)

def save_live_cluster_state(state):
    with open(CLUSTER_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def reconcile():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [GITOPS-OPERATOR] Starting Reconciliation Loop...")
    commit_hash, commit_msg = get_git_head_info()
    desired = load_desired_state()
    live = load_live_cluster_state()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [GITOPS-OPERATOR] Git Source of Truth Commit: {commit_hash} (\"{commit_msg}\")")

    if not desired:
        print("[ERROR] No desired state found in Git repository!")
        return

    desired_spec = desired.get("spec", {})
    desired_replicas = desired_spec.get("replicas")
    desired_image = desired_spec.get("template", {}).get("spec", {}).get("containers", [{}])[0].get("image")

    live_replicas = live.get("replicas")
    live_image = live.get("image")
    live_status = live.get("sync_status", "UNKNOWN")

    print(f"Desired State (Git): Replicas = {desired_replicas}, Image = {desired_image}")
    print(f"Live State (Cluster): Replicas = {live_replicas}, Image = {live_image}")

    # Check for Drift
    drift_detected = False
    diffs = []
    if desired_replicas != live_replicas:
        drift_detected = True
        diffs.append(f"Replicas mismatch: Live={live_replicas} vs Desired={desired_replicas}")
    if desired_image != live_image:
        drift_detected = True
        diffs.append(f"Image mismatch: Live={live_image} vs Desired={desired_image}")

    if drift_detected:
        print(f"--> [DRIFT DETECTED] Cluster out of sync with Git! Detected diffs: {diffs}")
        print("--> [RECONCILING] Applying declarative configuration to live cluster...")
        # Continuous Reconciliation
        time.sleep(0.5)
        new_live_state = {
            "name": desired["metadata"]["name"],
            "namespace": desired["metadata"]["namespace"],
            "replicas": desired_replicas,
            "image": desired_image,
            "sync_status": "Synced",
            "last_synced_commit": commit_hash,
            "last_sync_timestamp": datetime.now().isoformat()
        }
        save_live_cluster_state(new_live_state)
        print("--> [SUCCESS] Live cluster state reconciled. Status: Synced (Healthy)")
    else:
        print("--> [IN SYNC] Cluster matches Git source of truth perfectly. No action required.")

if __name__ == "__main__":
    try:
        import yaml
    except ImportError:
        pass
    reconcile()
