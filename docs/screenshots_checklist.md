# ContactHub — Screenshots Checklist for Project Report & Lab Record

Use this checklist to capture and organize the 15 required screenshots for your college project report, practical presentation slides, and lab record.

---

| # | Screenshot Title | Component / Module | How to Reproduce & Capture | Status |
| :-: | :--- | :--- | :--- | :-: |
| **1** | **Homepage / Landing Page** | Application UI | Open browser at `http://127.0.0.1:5000/`. Shows hero banner, features, and syllabus module breakdown. | [ ] |
| **2** | **Registration & Login Pages** | Authentication | Navigate to `/register` and `/login`. Shows form fields and demo auto-fill button. | [ ] |
| **3** | **Contact Dashboard Overview** | Core Dashboard | Log in as `demo@contacthub.local`. Displays total metrics, category progress bars, and recent contacts. | [ ] |
| **4** | **Add & Edit Contact Forms** | Contact CRUD | Navigate to `/contacts/new` and `/contacts/1/edit`. Shows contact fields, category dropdown, and favorite switch. | [ ] |
| **5** | **Search & Category Filter Results** | Search Engine | Navigate to `/contacts?q=DevOps` or `/contacts?category=Work`. Shows filtered contact cards and category tabs. | [ ] |
| **6** | **CSV Export & Import Interface** | Import/Export | Navigate to `/export` and `/import`. Shows CSV upload interface with duplicate policy radio options. | [ ] |
| **7** | **Docker Image Build Output** | Module 3: Docker | Run `docker images` in Windows PowerShell. Displays `contacthub:v1.0` image repository, tag, and size. | [ ] |
| **8** | **Running Docker Container** | Module 3: Docker | Run `docker ps` in Windows PowerShell. Shows container `contacthub-app` up and port mapped to `0.0.0.0:5000->5000/tcp`. | [ ] |
| **9** | **Container Health Check Status** | Module 3: Docker | Run `docker inspect --format='{{json .State.Health}}' contacthub-app` or open `http://localhost:5000/health`. | [ ] |
| **10** | **Minikube Node Status** | Module 4: Kubernetes | Run `kubectl get nodes` in Windows PowerShell. Shows active Minikube master/worker node in `Ready` status. | [ ] |
| **11** | **Kubernetes Pods & Deployment** | Module 4: Kubernetes | Run `kubectl get pods,deployments -n contacthub`. Shows `contacthub-deployment` with 1/1 ready pods. | [ ] |
| **12** | **Kubernetes Services (NodePort)** | Module 4: Kubernetes | Run `kubectl get services -n contacthub`. Shows `contacthub-service` (ClusterIP) and `contacthub-nodeport` (Port 30080). | [ ] |
| **13** | **Pod Scaling or Rolling Update** | Module 4: Kubernetes | Run `kubectl scale deployment contacthub-deployment --replicas=3 -n contacthub` and `kubectl get pods -n contacthub`. | [ ] |
| **14** | **AWS Lambda Local Test Output** | Module 5: Serverless | Run `python serverless/test_local.py`. Shows 4/4 passing test results and JSON payloads for Function A & B. | [ ] |
| **15** | **Automated Pytest Results** | Testing & QA | Run `python -m pytest` in project root. Shows `23 passed in xx.xxs` green test summary bar. | [ ] |

---

## Tips for Project Report Formatting
1. Use Windows Snipping Tool (`Windows + Shift + S`) to capture clean window screenshots.
2. Label each image in your report with a descriptive caption (e.g., *Figure 4.2: Kubernetes Pods Running in contacthub Namespace*).
3. Ensure terminal screenshots have clear, readable fonts with good contrast.
