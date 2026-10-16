# ContactHub Kubernetes Orchestration Guide (Module 4)

This directory contains production-ready Kubernetes manifests designed for deploying **ContactHub** to a local Kubernetes cluster (Minikube or Docker Desktop Kubernetes) or a cloud-managed Kubernetes cluster (AWS EKS, GKE, AKS).

---

## 1. Architecture Overview

```
+-------------------------------------------------------------+
|                     Kubernetes Cluster                      |
|                                                             |
|  Namespace: contacthub                                      |
|                                                             |
|  +---------------------+        +------------------------+  |
|  | contacthub-config   |        | contacthub-secret      |  |
|  | (ConfigMap)         |        | (Secret)               |  |
|  +----------+----------+        +-----------+------------+  |
|             |                               |               |
|             v                               v               |
|  +-------------------------------------------------------+  |
|  | Deployment: contacthub-deployment (1 Replica)        |  |
|  |                                                       |  |
|  | +---------------------------------------------------+ |  |
|  | | Pod: contacthub-xxxx-yyyy                         | |  |
|  | |   - Container: contacthub:v1.0 (Port 5000)        | |  |
|  | |   - Probes: /health (Liveness & Readiness)        | |  |
|  | |   - Storage: Volume mounted to /app/database      | |  |
|  | +---------------------------------------------------+ |  |
|  +---------------------------+---------------------------+  |
|                              |                              |
|                              v                              |
|  +-------------------------------------------------------+  |
|  | Service: contacthub-service (ClusterIP: 5000)         |  |
|  | Service: contacthub-nodeport (NodePort: 30080)        |  |
|  +-------------------------------------------------------+  |
+-------------------------------------------------------------+
                               |
                               v
                     Host Web Browser (Port 30080)
```

### Components

1. **Namespace (`namespace.yaml`)**: Isolates ContactHub resources inside the `contacthub` logical workspace.
2. **ConfigMap (`configmap.yaml`)**: Centralizes non-sensitive environment variables (`PORT`, `FLASK_DEBUG`, `DATABASE_PATH`).
3. **Secret (`secret.yaml.example`)**: Shields sensitive tokens (`SECRET_KEY`) from version control.
4. **PersistentVolumeClaim (`pvc.yaml`)**: Requests persistent disk storage for the SQLite database file.
5. **Deployment (`deployment.yaml`)**: Manages Pod replicas, rolling updates (`RollingUpdate`), resource boundaries (`requests` and `limits`), and automated health probes.
6. **Services (`service.yaml`)**: Exposes the application internally via `ClusterIP` and externally to the developer machine via `NodePort: 30080`.

---

## 2. Prerequisites on Windows

- **Docker Desktop** installed and running with Kubernetes enabled, OR **Minikube** installed.
- **kubectl** CLI installed.

Verify CLI tools in Windows PowerShell:

```powershell
kubectl version --client
minikube version  # If using Minikube
```

---

## 3. Step-by-Step Deployment Workflow

### Step 1: Start Minikube Cluster (if using Minikube)

```powershell
minikube start --driver=docker
kubectl get nodes
```

### Step 2: Build and Load Docker Image into Minikube

Build the Docker image locally:

```powershell
docker build -t contacthub:v1.0 .
```

If using Minikube, load the image directly into Minikube's Docker cache so it does not attempt to pull from external registries:

```powershell
minikube image load contacthub:v1.0
```

*(If using Docker Desktop Kubernetes, the image built via Docker CLI is immediately available without loading).*

### Step 3: Create the Secret from Template

Create your active secret manifest:

```powershell
Copy-Item kubernetes/secret.yaml.example kubernetes/secret.yaml
```

*(Edit `kubernetes/secret.yaml` if you want a custom secret key).*

### Step 4: Apply Manifests in Logical Order

Apply all manifests into the cluster:

```powershell
# 1. Create Namespace
kubectl apply -f kubernetes/namespace.yaml

# 2. Apply ConfigMap and Secret
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml

# 3. Apply Persistent Volume Claim
kubectl apply -f kubernetes/pvc.yaml

# 4. Apply Deployment and Services
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### Step 5: Verify Deployment and Pod Health

Check status across all components in the `contacthub` namespace:

```powershell
kubectl get pods -n contacthub
kubectl get deployments -n contacthub
kubectl get services -n contacthub
kubectl get pvc -n contacthub
```

Check logs of the running container:

```powershell
kubectl logs -l app=contacthub -n contacthub --tail=50
```

Describe deployment for detailed event logs and probe checks:

```powershell
kubectl describe deployment contacthub-deployment -n contacthub
```

### Step 6: Access the Application in Browser

- **On Docker Desktop Kubernetes:** Open your browser and navigate to:
  ```
  http://localhost:30080
  ```
- **On Minikube:** Run the service tunnel command:
  ```powershell
  minikube service contacthub-nodeport -n contacthub
  ```
  Or check the Minikube IP:
  ```powershell
  $MINIKUBE_IP = minikube ip
  Write-Host "Open: http://$MINIKUBE_IP:30080"
  ```

---

## 4. Demonstration Practicals for College Viva

### A. Horizontal Scaling Demonstration

Demonstrate scaling the deployment to 3 replicas:

```powershell
kubectl scale deployment contacthub-deployment --replicas=3 -n contacthub
kubectl get pods -n contacthub -w
```

> **Important Note on SQLite and Multi-Replica Pods:**
> SQLite is a local file-based database stored inside the container or mounted volume. Multiple pods attempting simultaneous concurrent writes to an independent SQLite file may encounter locking or data synchronization issues. For a single replica on a laptop, SQLite is fast, lightweight, and zero-configuration. When architecting high-scale horizontal multi-replica deployments in enterprise clouds, the stateless web layer is connected to a shared network database such as PostgreSQL or Amazon RDS.

Scale back to 1 replica after demonstrating:

```powershell
kubectl scale deployment contacthub-deployment --replicas=1 -n contacthub
```

### B. Rolling Update and Rollback Demonstration

Update the deployment with a new image tag:

```powershell
# Apply rolling update to v1.1
kubectl set image deployment/contacthub-deployment contacthub=contacthub:v1.1 -n contacthub

# Monitor rolling update progression
kubectl rollout status deployment/contacthub-deployment -n contacthub

# Inspect rollout revision history
kubectl rollout history deployment/contacthub-deployment -n contacthub

# Perform instant zero-downtime rollback to previous stable version
kubectl rollout undo deployment/contacthub-deployment -n contacthub

# Confirm rollback succeeded
kubectl rollout status deployment/contacthub-deployment -n contacthub
```

---

## 5. Teardown / Cleanup Commands

To remove all created ContactHub Kubernetes resources cleanly:

```powershell
kubectl delete namespace contacthub
```
