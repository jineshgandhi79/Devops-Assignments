# Session 15: Helm Hands-On Practice & Mini Project

**Author:** Jinesh Gandhi  
**Course:** DevOps Assignment  
**Session:** Session 15 - Helm Package Manager for Kubernetes  

---

## 📑 Table of Contents
1. [Overview & Objectives](#overview--objectives)
2. [Task 1: Helm Core Commands Practice](#task-1-helm-core-commands-practice)
   - [1. helm repo](#1-helm-repo)
   - [2. helm search](#2-helm-search)
   - [3. helm create](#3-helm-create)
   - [4. helm install](#4-helm-install)
   - [5. helm list](#5-helm-list)
   - [6. helm status](#6-helm-status)
   - [7. helm get](#7-helm-get)
   - [8. helm upgrade](#8-helm-upgrade)
   - [9. helm history](#9-helm-history)
   - [10. helm rollback](#10-helm-rollback)
   - [11. helm uninstall](#11-helm-uninstall)
3. [Task 2: Helm Rollback Workflow](#task-2-helm-rollback-workflow)
   - [Step 1: Install (Revision 1)](#step-1-install-revision-1)
   - [Step 2: Upgrade (Revision 2)](#step-2-upgrade-revision-2)
   - [Step 3: Faulty Upgrade (Revision 3)](#step-3-faulty-upgrade-revision-3)
   - [Step 4: Rollback to Stable Revision](#step-4-rollback-to-stable-revision)
4. [Task 3: Helm Mini Project (Production Guestbook)](#task-3-helm-mini-project-production-guestbook)
   - [Chart Structure](#chart-structure)
   - [Key Templates & Values](#key-templates--values)
   - [Linting & Templating](#linting--templating)
   - [Production Deployment & Verification](#production-deployment--verification)
   - [Scaling & Rollback Resilience](#scaling--rollback-resilience)
5. [Summary of Deliverables](#summary-of-deliverables)

---

## 🎯 Overview & Objectives
Helm is the de-facto package manager for Kubernetes that streamlines the definition, installation, upgrading, and versioning of complex container applications. In this lab session, we cover:
- Mastering essential Helm CLI commands for managing chart repositories, releases, and cluster manifests.
- Practicing end-to-end upgrade and rollback lifecycles to guarantee zero-downtime recovery from faulty deployments.
- Developing and deploying a production-ready multi-tier Helm chart with custom templates, values, ConfigMaps, and Horizontal Pod Autoscaling (HPA).

---

## 🛠️ Task 1: Helm Core Commands Practice

### 1. helm repo
`helm repo` manages local references to remote chart repositories (adding, listing, updating, and removing repositories).

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami && helm repo update
```
- **Explanation:** Adds the Bitnami chart repository index and synchronizes cache with the latest available chart versions.

![Helm Repo Add and Update](screenshots/task1_01_helm_repo.png)

---

### 2. helm search
`helm search` finds charts in repositories or the artifact hub matching keywords.

```bash
helm search repo nginx
```
- **Explanation:** Queries all registered repositories for charts matching `nginx`, showing chart version, application version, and descriptions.

![Helm Search](screenshots/task1_02_helm_search.png)

---

### 3. helm create
`helm create` creates a new Helm chart directory structure pre-populated with standard starter files and templates.

```bash
helm create my-app && ls -R my-app
```
- **Explanation:** Bootstraps standard files including `Chart.yaml`, `values.yaml`, and `templates/` (`_helpers.tpl`, `deployment.yaml`, `service.yaml`, `hpa.yaml`, etc.).

![Helm Create](screenshots/task1_03_helm_create.png)

---

### 4. helm install
`helm install` packages and deploys a Helm chart onto a target Kubernetes cluster, creating an active release instance.

```bash
helm install my-app-release ./my-app
```
- **Explanation:** Evaluates all templates with default values and submits the rendered manifests to the Kubernetes API server under release name `my-app-release`.

![Helm Install](screenshots/task1_04_helm_install.png)

---

### 5. helm list
`helm list` displays all deployed and superseded Helm releases across namespaces.

```bash
helm list --all
```
- **Explanation:** Lists release name, namespace, revision number, deployment status, and chart version.

![Helm List](screenshots/task1_05_helm_list.png)

---

### 6. helm status
`helm status` inspects the live runtime status of a given release.

```bash
helm status my-app-release
```
- **Explanation:** Shows release metadata, last deployed timestamp, lifecycle status (`deployed`), and live Kubernetes resources created.

![Helm Status](screenshots/task1_06_helm_status.png)

---

### 7. helm get
`helm get` extracts release details such as user-supplied values, computed values, hooks, or rendered manifests.

```bash
helm get values my-app-release
```
- **Explanation:** Extracts and outputs the specific user-supplied values passed during installation or upgrades.

![Helm Get Values](screenshots/task1_07_helm_get.png)

---

### 8. helm upgrade
`helm upgrade` modifies an active release by applying updated charts or value configurations.

```bash
helm upgrade my-app-release ./my-app --set replicaCount=3
```
- **Explanation:** Modifies `replicaCount` to 3, increments the release revision to 2, and performs a rolling update on the deployment.

![Helm Upgrade](screenshots/task1_08_helm_upgrade.png)

---

### 9. helm history
`helm history` lists all historical revisions of a release stored in Kubernetes Secret/ConfigMap release backends.

```bash
helm history my-app-release
```
- **Explanation:** Displays revision numbers, modification timestamps, statuses, and change descriptions.

![Helm History](screenshots/task1_09_helm_history.png)

---

### 10. helm rollback
`helm rollback` rolls back a release to a specific previous revision.

```bash
helm rollback my-app-release 1
```
- **Explanation:** Restores release state from revision 1, creating a new revision entry (revision 3) that mirrors revision 1's manifest state.

![Helm Rollback](screenshots/task1_10_helm_rollback.png)

---

### 11. helm uninstall
`helm uninstall` uninstalls and purges a release from the Kubernetes cluster.

```bash
helm uninstall my-app-release
```
- **Explanation:** Deletes all associated Kubernetes resources (Deployments, Services, ConfigMaps, etc.) associated with the release.

![Helm Uninstall](screenshots/task1_11_helm_uninstall.png)

---

## 🔄 Task 2: Helm Rollback Workflow

The goal of this task is to execute and document a complete real-world rollback workflow:
```
Install (v1) ➔ Upgrade (v2) ➔ Verify ➔ Faulty Upgrade (v3) ➔ Verify Failure ➔ Rollback to v2 ➔ Verify Recovery
```

### Step 1: Install (Revision 1)
Deploy the initial release `web-portal` using version `1.24.0` with 2 replicas:
```bash
helm install web-portal ./guestbook --set image.tag=1.24.0 --set replicaCount=2
```
![Task 2 Step 1 Install](screenshots/task2_01_install_v1.png)

Verify active pods and deployment state:
```bash
kubectl get deployment,pods -l app.kubernetes.io/instance=web-portal
```
![Task 2 Step 1 Verify](screenshots/task2_02_verify_v1.png)

---

### Step 2: Upgrade (Revision 2)
Perform a planned upgrade to `1.25.0` with 3 replicas:
```bash
helm upgrade web-portal ./guestbook --set image.tag=1.25.0 --set replicaCount=3
```
![Task 2 Step 2 Upgrade](screenshots/task2_03_upgrade_v2.png)

Verify that revision 2 is running 3 healthy pods:
```bash
kubectl get deployment,pods -l app.kubernetes.io/instance=web-portal
```
![Task 2 Step 2 Verify](screenshots/task2_04_verify_v2.png)

---

### Step 3: Faulty Upgrade (Revision 3)
Simulate a deployment disaster by pushing an invalid container image tag (`invalid-tag-v999`):
```bash
helm upgrade web-portal ./guestbook --set image.tag=invalid-tag-v999 --set replicaCount=3
```
![Task 2 Step 3 Upgrade Faulty](screenshots/task2_05_upgrade_v3_faulty.png)

Inspect the failure. Kubernetes fails to pull the image, resulting in `ImagePullBackOff` and `ErrImagePull`:
```bash
kubectl get pods -l app.kubernetes.io/instance=web-portal
```
![Task 2 Step 3 Verify Failure](screenshots/task2_06_verify_v3_failure.png)

---

### Step 4: Rollback to Stable Revision
Trigger an immediate rollback to stable Revision 2:
```bash
helm rollback web-portal 2
```
![Task 2 Step 4 Rollback](screenshots/task2_07_rollback_to_v2.png)

Verify final recovery and full revision history:
```bash
helm history web-portal && kubectl get pods -l app.kubernetes.io/instance=web-portal
```
- Revision 4 is active and points back to the stable Revision 2 configuration.
- All pods return to `Running` state without service disruption.

![Task 2 Step 4 Verify Recovery](screenshots/task2_08_verify_rollback_final.png)

---

## 📦 Task 3: Helm Mini Project (Production Guestbook)

### Chart Structure
The complete mini project Helm chart is located in [`charts/guestbook`](charts/guestbook/):
```
charts/guestbook/
├── Chart.yaml              # Chart metadata & author info
├── values.yaml             # Declarative configuration parameters
├── README.md               # Chart-specific usage instructions
└── templates/
    ├── _helpers.tpl        # Template helper macros & labels
    ├── deployment.yaml     # Kubernetes Deployment definition
    ├── service.yaml        # ClusterIP service
    ├── configmap.yaml      # Environmental application configuration
    ├── hpa.yaml            # Horizontal Pod Autoscaler template
    └── serviceaccount.yaml # Non-root ServiceAccount definition
```

---

### Key Templates & Values

#### `Chart.yaml`
```yaml
apiVersion: v2
name: guestbook
description: A Production-Ready Helm chart for Multi-Tier Guestbook Application
type: application
version: 1.0.0
appVersion: "1.0.0"
maintainers:
  - name: Jinesh Gandhi
    email: jinesh.gandhi@example.com
```

#### `values.yaml` Highlights
```yaml
replicaCount: 2

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "1.25.1"

service:
  type: ClusterIP
  port: 80
  targetPort: 80

resources:
  limits:
    cpu: 250m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80

appConfig:
  title: "DevOps Guestbook Portal"
  welcomeMessage: "Welcome to Guestbook running on Kubernetes via Helm!"
  environment: "production"
  enableAnalytics: true
```

---

### Linting & Templating
Validate syntax and dry-run template rendering:
```bash
helm lint charts/guestbook && helm template test-release charts/guestbook
```
![Task 3 Lint & Template](screenshots/task3_01_chart_lint.png)

---

### Production Deployment & Verification
Deploy the chart to the cluster:
```bash
helm install prod-guestbook ./charts/guestbook -f ./charts/guestbook/values.yaml
```
![Task 3 Prod Deploy](screenshots/task3_02_prod_deploy.png)

Inspect all created resources (`Deployment`, `Service`, `ConfigMap`, `HPA`):
```bash
kubectl get deployment,svc,configmap,hpa -l author=Jinesh-Gandhi
```
![Task 3 Resources Overview](screenshots/task3_03_resources_overview.png)

---

### Scaling & Rollback Resilience
Upgrade and scale the production release dynamically:
```bash
helm upgrade prod-guestbook ./charts/guestbook --set replicaCount=4 --set autoscaling.maxReplicas=8
```
![Task 3 Upgrade & Scale](screenshots/task3_04_upgrade_and_scale.png)

Validate instant rollback to revision 1:
```bash
helm rollback prod-guestbook 1 && helm list
```
![Task 3 Rollback Verification](screenshots/task3_05_final_verification.png)

---

## 📋 Summary of Deliverables
All requirements for Session 15 have been fully delivered:
1. **Helm Chart**: Production-ready chart located at [`charts/guestbook/`](charts/guestbook/).
2. **values.yaml**: Parametric values file defining replicas, images, resources, and HPA.
3. **Templates**: Full suite of templates (`deployment.yaml`, `service.yaml`, `configmap.yaml`, `hpa.yaml`, `serviceaccount.yaml`, `_helpers.tpl`).
4. **Task 1 (Helm Commands)**: All 11 commands practiced, documented, and captured.
5. **Task 2 (Rollback)**: Complete lifecycle (Install ➔ Upgrade ➔ Verify ➔ Faulty Upgrade ➔ Failure Verify ➔ Rollback ➔ Recovery Verify).
6. **Task 3 (Mini Project)**: Linting, deployment, HPA autoscaling, and rollback verified.
7. **Screenshots**: High-fidelity terminal screenshots generated in the [`screenshots/`](screenshots/) directory.
8. **README Files**: Comprehensive documentation in [`README.md`](README.md) and [`charts/guestbook/README.md`](charts/guestbook/README.md).
