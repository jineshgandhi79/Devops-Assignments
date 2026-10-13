# Session 12: Kubernetes Ingress, ConfigMaps & Secrets

**Author:** Jinesh Gandhi  
**Course:** DevOps Hands-On Engineering  
**Lab Environment:** Kubernetes v1.28+, NGINX Ingress Controller, Linux Terminal Node  

---

## Table of Contents
1. [Overview & Architecture](#overview--architecture)
2. [Task 1: ConfigMap Hands-On](#task-1-configmap-hands-on)
   - [ConfigMap Manifest & Creation](#11-configmap-manifest--creation)
   - [Injecting ConfigMap into Pod & Verification](#12-injecting-configmap-into-pod--verification)
3. [Task 2: Kubernetes Secret Hands-On](#task-2-kubernetes-secret-hands-on)
   - [Secret Manifest & Base64 Inspection](#21-secret-manifest--base64-inspection)
   - [Injecting Secret into Pod & Volume Verification](#22-injecting-secret-into-pod--volume-verification)
   - [Why Secrets Should NOT Be Committed Directly to Git](#23-why-secrets-should-not-be-committed-directly-to-git)
4. [Task 3: Ingress Routing Hands-On](#task-3-ingress-routing-hands-on)
   - [Deploying Application & Service](#31-deploying-application--service)
   - [Configuring Ingress Resource](#32-configuring-ingress-resource)
   - [Accessing Application & Verifying Traffic](#33-accessing-application--verifying-traffic)
5. [Task 4: Ingress vs Ingress Controller](#task-4-ingress-vs-ingress-controller)
   - [What is Ingress?](#41-what-is-ingress)
   - [What is an Ingress Controller?](#42-what-is-an-ingress-controller)
   - [Key Differences](#43-key-differences)
   - [Why Both Are Required](#44-why-both-are-required)
   - [Real-World Architecture Examples](#45-real-world-architecture-examples)
6. [Task 5: Troubleshooting Scenario](#task-5-troubleshooting-scenario)
   - [Problem Identification & Diagnosis (Before Fix)](#51-problem-identification--diagnosis-before-fix)
   - [Root Cause Analysis](#52-root-cause-analysis)
   - [Remediation & Resolution (After Fix)](#53-remediation--resolution-after-fix)
7. [Repository Manifest Artifacts](#repository-manifest-artifacts)

---

## Overview & Architecture

This lab covers three foundational pillars of modern Kubernetes microservice architecture:
- **ConfigMaps:** Externalizing non-confidential application configuration from container images.
- **Secrets:** Safely storing, encoding, and mounting sensitive credentials (API keys, database passwords, SSL certificates).
- **Ingress & Ingress Controllers:** Providing Layer 7 (HTTP/HTTPS) routing, reverse proxying, and SSL termination for cluster workloads.

```mermaid
flowchart TD
    Client(["External Client / Browser"]) -->|HTTP Host: myapp.local| IC["Ingress Controller (NGINX)"]
    IR["Ingress Resource (Rules)"] -.->|Configures| IC
    IC -->|Reverse Proxy / L7 Route| Svc["ClusterIP Service: web-app-service"]
    Svc --> Pod1["Pod Replica 1"]
    Svc --> Pod2["Pod Replica 2"]
    
    CM["ConfigMap: app-config"] -->|Env Vars & File Mount| Pod1
    SEC["Secret: app-secret"] -->|Env Vars & Read-Only Volume| Pod1
    CM -->|Env Vars & File Mount| Pod2
    SEC -->|Env Vars & Read-Only Volume| Pod2
```

---

## Task 1: ConfigMap Hands-On

### 1.1 ConfigMap Manifest & Creation
ConfigMaps decouple environment configuration artifacts from image builds, making applications portable across staging, testing, and production without rebuilding containers.

Manifest file: [01-configmap.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/01-configmap.yaml)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  labels:
    app: demo-app
data:
  APP_ENV: "production"
  APP_PORT: "8080"
  LOG_LEVEL: "info"
  WELCOME_MESSAGE: "Hello from Kubernetes ConfigMap! Configured for DevOps Session 12."
  app.properties: |
    database.host=db.internal.local
    database.port=5432
    cache.ttl=3600
    feature.dark_mode=true
```

Apply and inspect the ConfigMap:
```bash
kubectl apply -f manifests/01-configmap.yaml
kubectl get configmaps
kubectl describe configmap app-config
```

![Task 1 ConfigMap Creation](screenshots/01-create-configmap.png)

---

### 1.2 Injecting ConfigMap into Pod & Verification
A ConfigMap can be consumed inside a Pod in two primary ways:
1. **Environment Variables:** Direct key injection using `valueFrom.configMapKeyRef`.
2. **Volume Mounts:** Mounted as files inside a directory using `volumes.configMap` and `volumeMounts`.

Manifest file: [02-pod-configmap.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/02-pod-configmap.yaml)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod-configmap
  labels:
    app: demo-app
spec:
  containers:
  - name: web-container
    image: nginx:alpine
    ports:
    - containerPort: 80
    env:
    - name: APP_ENV
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: APP_ENV
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
    - name: APP_MESSAGE
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: WELCOME_MESSAGE
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
      readOnly: true
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

Verify injected environment variables and mounted configuration files:
```bash
kubectl apply -f manifests/02-pod-configmap.yaml
kubectl get pods demo-pod-configmap
kubectl exec demo-pod-configmap -- env | grep -E 'APP_|LOG_'
kubectl exec demo-pod-configmap -- cat /etc/config/app.properties
```

![Task 1 Pod ConfigMap Verification](screenshots/02-pod-configmap-verify.png)

---

## Task 2: Kubernetes Secret Hands-On

### 2.1 Secret Manifest & Base64 Inspection
Kubernetes Secrets store sensitive configuration such as credentials, access tokens, and private keys. Kubernetes stores secret values as Base64-encoded strings.

Manifest file: [03-secret.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/03-secret.yaml)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
  labels:
    app: demo-app
type: Opaque
stringData:
  DB_USERNAME: "db_admin_jinesh"
  DB_PASSWORD: "SuperSecurePassword2026!"
  API_KEY: "ak_live_99f8e4a7b21c0d5e89a312"
  jwt_secret.key: |
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA0Y3d+JineshDevOpsSession12SampleKey...
    -----END RSA PRIVATE KEY-----
```

Apply the secret and inspect base64 encoding:
```bash
kubectl apply -f manifests/03-secret.yaml
kubectl get secrets
kubectl describe secret app-secret
kubectl get secret app-secret -o jsonpath='{.data.DB_USERNAME}'
echo 'ZGJfYWRtaW5famluZXNo' | base64 --decode
```

![Task 2 Secret Creation](screenshots/03-create-secret.png)

---

### 2.2 Injecting Secret into Pod & Volume Verification
Injecting Secrets into a Pod via environment variables and read-only volumes (with strict file permissions `0400`):

Manifest file: [04-pod-secret.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/04-pod-secret.yaml)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod-secret
  labels:
    app: demo-app
spec:
  containers:
  - name: secured-container
    image: nginx:alpine
    ports:
    - containerPort: 80
    env:
    - name: DATABASE_USER
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_USERNAME
    - name: DATABASE_PASS
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_PASSWORD
    - name: APP_API_KEY
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: API_KEY
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: app-secret
      defaultMode: 0400
```

Verify secrets inside the container:
```bash
kubectl apply -f manifests/04-pod-secret.yaml
kubectl get pods demo-pod-secret
kubectl exec demo-pod-secret -- env | grep -E 'DATABASE_|APP_API'
kubectl exec demo-pod-secret -- ls -la /etc/secrets
kubectl exec demo-pod-secret -- cat /etc/secrets/DB_USERNAME
```

![Task 2 Pod Secret Verification](screenshots/04-pod-secret-verify.png)

---

### 2.3 Why Secrets Should NOT Be Committed Directly to Git

> [!CAUTION]
> **Base64 is NOT Encryption**: Base64 is merely an encoding algorithm designed for data transport. Anyone who reads a base64 string can instantly decode it using `base64 --decode`.

1. **Git Commit History is Immutable**: Once a secret is committed to a Git repository, it remains in git history indefinitely across commits, branches, and tags. Even if deleted in a subsequent commit, attackers can easily retrieve it via `git log -p` or commit trees.
2. **Access Control Leakage**: Developers, contractors, CI/CD runners, and automated bots who have read access to the repository gain instant access to production passwords and private keys.
3. **Automated Scraping Bots**: Public and internal repositories are continuously monitored by malicious scanners (e.g., Trufflehog, GitGuardian, Shodan). Exposed tokens can be compromised within minutes of pushing.
4. **Best Practices for Secrets Management**:
   - **Sealed Secrets (Bitnami)**: Uses asymmetric public-key cryptography where only the cluster's private key can decrypt the secret. Sealed secrets can be safely committed to Git.
   - **External Secrets Operator (ESO)**: Synchronizes secrets securely from HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager directly into native Kubernetes Secrets.
   - **Mozilla SOPS & Age**: Encrypts values in YAML files before git commit.
   - **Git Pre-commit Hooks**: Use tools like `gitleaks` to block commits containing API keys and passwords.

---

## Task 3: Ingress Routing Hands-On

### 3.1 Deploying Application & Service
Ingress works in conjunction with a ClusterIP Service that fronts container pods.

Manifest file: [05-app-and-service.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/05-app-and-service.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-deployment
  labels:
    app: web-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: nginxdemos/hello:plain-text
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
  labels:
    app: web-app
spec:
  type: ClusterIP
  selector:
    app: web-app
  ports:
  - name: http
    port: 80
    targetPort: 80
```

Deploy application and inspect endpoints:
```bash
kubectl apply -f manifests/05-app-and-service.yaml
kubectl get deployments,pods,svc -l app=web-app
kubectl get endpoints web-app-service
```

![Task 3 Deploy App and Service](screenshots/05-deploy-app-service.png)

---

### 3.2 Configuring Ingress Resource
An Ingress resource defines Layer 7 HTTP routing rules matching hosts and URI paths to backend services.

Manifest file: [06-ingress.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/06-ingress.yaml)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 80
```

Apply Ingress and check controller status:
```bash
kubectl apply -f manifests/06-ingress.yaml
kubectl get ingress
kubectl describe ingress web-app-ingress
kubectl get pods -n ingress-nginx
```

![Task 3 Ingress Configuration](screenshots/06-ingress-config.png)

---

### 3.3 Accessing Application & Verifying Traffic
Sending HTTP requests through the Ingress controller IP (`192.168.49.2`) using the configured Host header (`Host: myapp.local`):

```bash
# Test 1: Route to application via Ingress Host rule
curl -i -H 'Host: myapp.local' http://192.168.49.2/

# Test 2: Consecutive request routed across replica pods
curl -s -H 'Host: myapp.local' http://192.168.49.2/ | grep 'Server name'

# Test 3: Unmatched host returns default HTTP 404
curl -i http://192.168.49.2/
```

![Task 3 Ingress Traffic Verification](screenshots/07-ingress-traffic-verify.png)

---

## Task 4: Ingress vs Ingress Controller

### 4.1 What is Ingress?
An **Ingress** is a standard Kubernetes API resource (`kind: Ingress`) that defines rules for routing external HTTP/HTTPS traffic to internal cluster services. It acts as a configuration blueprint specifying:
- **Host-based routing:** e.g., `api.example.com` vs `web.example.com`
- **Path-based routing:** e.g., `/users` vs `/orders`
- **TLS/SSL termination:** Mapping domain certificates to secrets.

> [!NOTE]
> Creating an Ingress resource on its own does **nothing**. It is purely data stored in the Kubernetes `etcd` database until an Ingress Controller processes it.

---

### 4.2 What is an Ingress Controller?
An **Ingress Controller** is an active daemon (running inside a Pod or cluster infrastructure) that continuously monitors the Kubernetes API server for Ingress resource changes, translates those rules into reverse proxy configuration (such as `nginx.conf` or Envoy route tables), and routes actual network packets.

Popular Ingress Controllers include:
- **ingress-nginx:** NGINX reverse proxy managed by the Kubernetes community.
- **Traefik:** Dynamic cloud-native edge router.
- **HAProxy Ingress:** High-performance proxy for extreme throughput.
- **AWS Load Balancer Controller:** Provisions AWS Application Load Balancers (ALB).

---

### 4.3 Key Differences

| Feature / Aspect | Ingress | Ingress Controller |
| :--- | :--- | :--- |
| **Type** | Kubernetes API Resource (Specification / YAML) | Active Application / Daemon (Pod / Reverse Proxy) |
| **Purpose** | Declares desired routing rules & hosts | Executes routing, manages traffic, handles SSL |
| **Default in Cluster** | Built into Kubernetes API schema | Must be installed separately (e.g. Helm, Minikube addon) |
| **Execution** | Passive data record in `etcd` | Active process processing network connections |
| **Analogy** | A architectural building blueprint | The construction team that builds and operates the building |

---

### 4.4 Why Both Are Required
1. **Separation of Concerns:** Application developers only need to define *what* routes their service needs using standard Ingress YAML files, without knowing what underlying reverse proxy is deployed.
2. **Infrastructure Decoupling:** Cluster administrators can swap the controller (e.g., migrate from NGINX to Traefik or AWS ALB) without changing application developer YAML manifests.
3. **Execution Reality:** Without an Ingress resource, the controller has no rules to route. Without a controller, the Ingress resource is an inactive configuration file.

---

### 4.5 Real-World Architecture Examples

#### Example 1: Path-Based Routing (Single Domain)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: company.com
    http:
      paths:
      - path: /billing
        pathType: Prefix
        backend:
          service:
            name: billing-svc
            port:
              number: 8080
      - path: /catalog
        pathType: Prefix
        backend:
          service:
            name: catalog-svc
            port:
              number: 3000
```

#### Example 2: Host-Based Routing with TLS
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-ingress
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - dashboard.company.com
    secretName: company-tls-cert
  rules:
  - host: dashboard.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dashboard-svc
            port:
              number: 80
```

---

## Task 5: Troubleshooting Scenario

The `troubleshooting/` directory contains an intentionally broken configuration scenario demonstrating common real-world Kubernetes deployment pitfalls.

### 5.1 Problem Identification & Diagnosis (Before Fix)

Broken manifest: [broken-manifest.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/troubleshooting/broken-manifest.yaml)

When applying the broken configuration:
```bash
kubectl apply -f troubleshooting/broken-manifest.yaml
kubectl get pods -l app=troubleshooting-app
kubectl describe pod <pod-name>
kubectl describe ingress troubleshooting-ingress
curl -i -H 'Host: troubleshoot.local' http://192.168.49.2/
```

**Observed Symptoms:**
1. Pod status stuck in **`CreateContainerConfigError`** (0/1 Ready).
2. Pod events display:
   - `Error: configmap "broken-app-config" key "DATABASE_URL" does not exist`
   - `Error: secret "auth-secret" not found`
3. Ingress backend reports: `<error: endpoints not found>`.
4. Ingress curl returns **`HTTP 503 Service Temporarily Unavailable`**.

![Task 5 Troubleshooting Before Fix](screenshots/08-troubleshooting-before.png)

---

### 5.2 Root Cause Analysis

1. **ConfigMap Key Mismatch:**
   - In `broken-manifest.yaml`, the ConfigMap `broken-app-config` defined data key `DB_URL`.
   - The Pod container environment spec referenced `key: DATABASE_URL`.
   - *Result:* Kubelet cannot resolve the key during container setup and aborts container creation.
2. **Missing Secret Resource:**
   - The Pod referenced `secretKeyRef: name: auth-secret`.
   - Secret `auth-secret` was never defined or applied to the cluster.
   - *Result:* Kubelet fails with `secret "auth-secret" not found`.
3. **Ingress Backend Port Mismatch:**
   - The Service `troubleshooting-service` was defined on port `80`.
   - The Ingress rule directed traffic to `service.port.number: 8080`.
   - *Result:* Ingress controller cannot find endpoints on port 8080 and responds with `HTTP 503 Service Temporarily Unavailable`.

---

### 5.3 Remediation & Resolution (After Fix)

Fixed manifest: [fixed-manifest.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/troubleshooting/fixed-manifest.yaml)

Key fixes implemented:
```diff
--- troubleshooting/broken-manifest.yaml
+++ troubleshooting/fixed-manifest.yaml
@@ -4,2 +4,2 @@
 data:
-  DB_URL: "postgres://db.prod.internal:5432/main"
+  DATABASE_URL: "postgres://db.prod.internal:5432/main"
+---
+apiVersion: v1
+kind: Secret
+metadata:
+  name: auth-secret
+type: Opaque
+stringData:
+  token: "dHJvdWJsZXNob290aW5nLXRva2VuLTIwMjY="
@@ -45,3 +54,4 @@
           service:
             name: troubleshooting-service
-            port:
-              number: 8080
+            port:
+              number: 80
```

Apply fixed manifest and verify:
```bash
kubectl apply -f troubleshooting/fixed-manifest.yaml
kubectl get pods -l app=troubleshooting-app
kubectl exec <pod-name> -- env | grep -E 'DATABASE_URL|SECRET_TOKEN'
kubectl describe ingress troubleshooting-ingress
curl -i -H 'Host: troubleshoot.local' http://192.168.49.2/
```

**Verification Results:**
- Pod status transitioned to **`Running` (1/1 Ready)**.
- Both `DATABASE_URL` and `SECRET_TOKEN` are populated in the container.
- Ingress resolved endpoints (`10.244.0.22:80`).
- HTTP request succeeded with **`HTTP 200 OK`**.

![Task 5 Troubleshooting After Fix](screenshots/09-troubleshooting-after.png)

---

## Repository Manifest Artifacts

All YAML configurations created and tested in this session are available in the workspace:

- [01-configmap.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/01-configmap.yaml): ConfigMap declaration.
- [02-pod-configmap.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/02-pod-configmap.yaml): Pod consuming ConfigMap via env and mounted volume.
- [03-secret.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/03-secret.yaml): Secret declaration with `stringData`.
- [04-pod-secret.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/04-pod-secret.yaml): Pod consuming Secret via env and `0400` read-only volume.
- [05-app-and-service.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/05-app-and-service.yaml): Web Deployment & ClusterIP Service.
- [06-ingress.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/manifests/06-ingress.yaml): Layer 7 Ingress routing manifest.
- [broken-manifest.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/troubleshooting/broken-manifest.yaml): Broken troubleshooting scenario.
- [fixed-manifest.yaml](file:///d:/Assignments/Devops%20Assignment/Session%2012/troubleshooting/fixed-manifest.yaml): Corrected troubleshooting manifest.

---
*Created by **Jinesh Gandhi** — DevOps Session 12 Lab Documentation*
