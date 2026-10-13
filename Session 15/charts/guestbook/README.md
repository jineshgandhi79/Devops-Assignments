# Helm Mini Project - Guestbook Production Stack

**Author:** Jinesh Gandhi  
**Session:** Session 15 - Helm  
**Version:** 1.0.0  

---

## 📌 Project Overview
The **Guestbook Production Stack** is a fully templated, production-grade Helm chart that orchestrates:
- **Scalable Deployment**: Configured with resource requests/limits, health probes, and non-root security contexts.
- **ClusterIP Service**: High-availability internal service routing.
- **ConfigMap**: Decoupled application environmental configuration.
- **Horizontal Pod Autoscaler (HPA)**: Automated metric-based autoscaling (target 80% CPU utilization).
- **ServiceAccount**: Isolated least-privilege security identity.

---

## 📂 Chart Directory Structure
```
charts/guestbook/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── _helpers.tpl
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    ├── hpa.yaml
    └── serviceaccount.yaml
```

---

## 🚀 Deployment Instructions

### 1. Lint and Validate the Chart
```bash
helm lint charts/guestbook
helm template my-test charts/guestbook
```

### 2. Install the Chart
```bash
helm install prod-guestbook ./charts/guestbook -f ./charts/guestbook/values.yaml
```

### 3. Upgrade with Dynamic Overrides
```bash
helm upgrade prod-guestbook ./charts/guestbook --set replicaCount=4 --set autoscaling.maxReplicas=8
```

### 4. Rollback Release
```bash
helm rollback prod-guestbook 1
```

### 5. Uninstall Release
```bash
helm uninstall prod-guestbook
```
