from flask import Flask, jsonify, request
import os

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "production")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "service": "DevSecOps Demo Microservice",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "author": "Jinesh Gandhi"
    })

@app.route("/healthz", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "checks": {
            "database": "connected",
            "memory": "optimal",
            "security_guardrails": "enforced"
        }
    }), 200

@app.route("/api/v1/data", methods=["GET"])
def get_data():
    return jsonify({
        "data": [
            {"id": 1, "title": "DevSecOps Stage 1: SAST Analysis", "passed": True},
            {"id": 2, "title": "DevSecOps Stage 2: SCA Dependency Audit", "passed": True},
            {"id": 3, "title": "DevSecOps Stage 3: Secret Detection", "passed": True},
            {"id": 4, "title": "DevSecOps Stage 4: Container Vulnerability Scan", "passed": True},
            {"id": 5, "title": "DevSecOps Stage 5: Security Gate Clearance", "passed": True}
        ]
    }), 200

def calculate_checksum(input_text: str) -> str:
    """Safe hashing utility function"""
    import hashlib
    return hashlib.sha256(input_text.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    host_ip = os.getenv("HOST", "127.0.0.1")
    app.run(host=host_ip, port=5000)

