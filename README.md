# ContactHub — Contact Management System
### BCA College Practical Microproject | Cloud Computing & DevOps Curriculum

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5?logo=kubernetes)
![AWS Lambda](https://img.shields.io/badge/AWS%20Lambda-Serverless-FF9900?logo=awslambda)
![Tests](https://img.shields.io/badge/Tests-23%2F23%20Passing-brightgreen?logo=pytest)

---

## 1. Project Overview

**ContactHub** is a modern, lightweight, full-stack contact management application designed specifically for a **Bachelor of Computer Applications (BCA)** final-year or semester microproject. 

It fulfills the academic requirements of all **5 Cloud Computing and DevOps syllabus modules**:
- **Module 1: Introduction to Virtualization** (Hypervisors, Ubuntu VM setup, snapshots, and cloning)
- **Module 2: Virtualization Tools & VM Automation** (KVM, QEMU, libvirt, virsh automation scripting)
- **Module 3: Containerization Using Docker** (Hardened non-root Dockerfile, persistent volume storage, Gunicorn, Docker Compose, Docker Hub registry)
- **Module 4: Container Orchestration with Kubernetes** (Minikube, Pods, Deployments, ReplicaSets, ClusterIP, NodePort, health probes, rolling updates, and rollbacks)
- **Module 5: Serverless Architecture using AWS Lambda & API Gateway** (FaaS, Event-driven architecture, API Gateway HTTP API, SAM template, local invocation)

---

## 2. Key Features

- **Authentication & Security:** User registration, password hashing (scrypt/pbkdf2), session management, CSRF protection, and strict user data isolation (blocking IDOR).
- **Dashboard:** Real-time statistics, category distribution progress bars, favorite VIP contacts, and recently added contacts.
- **Contact CRUD:** Add, view, edit, and delete contacts with initials-based colored avatars and deletion confirmation modals.
- **Multi-Field Search & Filter:** Instant search across Name, Phone, Email, Company, and City; filter by categories (Personal, Work, Family, Friends, Other) and favorite status.
- **Bulk CSV Import & Export:** Export authenticated user contacts to CSV; import contacts with duplicate handling options (`skip`, `update`, `allow_duplicates`).
- **Health Endpoint:** Production `/health` endpoint returning JSON service metadata and database connectivity status.

---

## 3. Project Directory Structure

```text
ContactHub/
├── app.py                      # Core Flask web application factory & routes
├── config.py                   # Development, testing, and production configuration
├── requirements.txt            # Python dependencies (Flask, pytest, gunicorn, etc.)
├── Dockerfile                  # Hardened multi-stage non-root container definition
├── docker-compose.yml          # Docker Compose with persistent SQLite volume
├── .dockerignore               # Build context exclusions
├── .gitignore                  # Git exclusions (database, cache, virtual environments)
├── .env.example                # Template for environment secrets
├── pytest.ini                  # Pytest configuration settings
├── README.md                   # Master project README
├── database/
│   ├── schema.sql              # Database schema DDL (users, contacts, tags, indexes)
│   ├── init_db.py              # SQLite initialization script
│   └── seed_data.py            # Fictional demo accounts and sample contacts
├── templates/
│   ├── base.html               # Master layout with responsive sidebar and topbar
│   ├── index.html              # Landing page highlighting features and modules
│   ├── register.html           # User registration form
│   ├── login.html              # User login form with quick demo auto-fill
│   ├── dashboard.html          # Analytics dashboard with metrics and progress bars
│   ├── contacts.html           # Contacts directory with search, filter, and pagination
│   ├── contact_detail.html     # Comprehensive single contact profile view
│   ├── contact_form.html       # Add / Edit contact form
│   ├── import_contacts.html    # CSV bulk import with duplicate detection policy
│   ├── export_contacts.html    # CSV export generator with data isolation assurance
│   ├── profile.html            # User account profile and password update form
│   ├── 404.html                # Friendly custom 404 error page
│   └── 500.html                # Friendly custom 500 error page
├── static/
│   ├── css/
│   │   └── style.css           # Custom navy/teal design theme and avatar classes
│   └── js/
│       └── main.js             # Mobile sidebar toggle, AJAX favorite stars, alerts
├── tests/
│   ├── conftest.py             # Isolated temporary database fixtures
│   ├── test_auth.py            # Registration, login, password security tests
│   ├── test_contacts.py        # Contact CRUD, search, filter, and user isolation tests
│   ├── test_import_export.py   # CSV import/export and duplicate handling tests
│   └── test_health.py          # /health API and homepage tests
├── scripts/
│   ├── setup.ps1               # Automated Windows setup script
│   ├── run.ps1                 # Automated Windows application runner
│   ├── test.ps1                # Automated full test suite runner (pytest + serverless)
│   ├── setup_kvm.sh            # Linux bash script: install and configure KVM/libvirt
│   └── manage_vm.sh            # Linux bash script: virsh VM lifecycle automation
├── kubernetes/
│   ├── namespace.yaml          # K8s namespace: contacthub
│   ├── configmap.yaml          # Non-sensitive configuration (Port, Debug, Database)
│   ├── secret.yaml.example     # Secret key template
│   ├── pvc.yaml                # Persistent volume claim for SQLite
│   ├── deployment.yaml         # Deployment with probes, limits, and rolling updates
│   ├── service.yaml            # ClusterIP and NodePort (Port 30080) services
│   └── README.md               # Complete Kubernetes & Minikube guide
├── serverless/
│   ├── lambda_function.py      # Function A: Contact Summary API handler
│   ├── contact_export_function.py # Function B: Export Request & S3 signer handler
│   ├── test_local.py           # Standalone local test harness (no AWS account needed)
│   ├── template.yaml           # AWS SAM Infrastructure as Code (IaC) template
│   └── README.md               # Complete AWS Serverless guide
└── docs/
    ├── architecture.md         # System architecture, ER diagram, and component design
    ├── module1-virtualization.md # Hypervisors, VirtualBox, Ubuntu VM setup, snapshots
    ├── module2-automation.md   # KVM, QEMU, libvirt, virsh automation scripting
    ├── module3-docker.md       # Dockerfile, Gunicorn, volumes, Docker Hub push/pull
    ├── module4-kubernetes.md   # Minikube, Pods, Deployments, Services, scaling, rollbacks
    ├── module5-serverless.md   # AWS Lambda, API Gateway, S3 pre-signed URLs, SAM CLI
    ├── project_report.md       # Full academic project report for college submission
    ├── viva_questions.md       # 25 beginner-friendly viva questions and answers
    └── screenshots_checklist.md # 15 essential screenshots checklist for lab records
```

---

## 4. Quick Start on Windows

### Prerequisites
- Python 3.10+ installed and added to PATH (`python --version`)
- Modern web browser (Chrome, Edge, Firefox)

### Option 1: Automated 1-Click PowerShell Setup
From Windows PowerShell in the `ContactHub` folder:

```powershell
# Run the automated setup script
.\scripts\setup.ps1

# Start the application
.\scripts\run.ps1
```

### Option 2: Manual Terminal Commands
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed development database with demo data
python database/seed_data.py

# 3. Start local development server
python app.py
```

Open your browser at: **`http://127.0.0.1:5000`**

### Pre-Seeded Demo Credentials for Testing & Viva
- **Email:** `demo@contacthub.local`
- **Password:** `Demo@12345`

*(You can also click the "Auto-Fill" button on the login screen for instant one-click login).*

---

## 5. Running Automated Tests

Run the complete test suite:

```powershell
# Run using the automated script
.\scripts\test.ps1

# Or run pytest directly
python -m pytest
```

### Actual Test Results (Verified)
- **Pytest:** `23 passed in 16.46s` (100% pass rate across auth, CRUD, user isolation, CSV import/export, and health check).
- **Serverless Local Tests:** `4/4 passed` (Function A summary API, Function B export handler, missing user ID validation, invalid format validation).

---

## 6. Running with Docker (Module 3)

Make sure Docker Desktop is running:

```powershell
# Build and run with Docker Compose (with persistent SQLite volume)
docker compose up -d --build

# Inspect running container
docker compose ps
docker compose logs

# Access in browser
Start-Process "http://localhost:5000"

# Stop container
docker compose down
```

---

## 7. Deploying to Kubernetes (Module 4)

Make sure Minikube or Docker Desktop Kubernetes is active:

```powershell
# Start Minikube cluster
minikube start --driver=docker

# Build and load image into Minikube
docker build -t contacthub:v1.0 .
minikube image load contacthub:v1.0

# Apply manifests
Copy-Item kubernetes/secret.yaml.example kubernetes/secret.yaml
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Verify pods
kubectl get pods -n contacthub
kubectl get services -n contacthub
```

Access via NodePort service: `http://localhost:30080` or `minikube service contacthub-nodeport -n contacthub`.

---

## 8. Serverless Testing (Module 5)

Test the AWS Lambda handlers locally on your laptop without needing an AWS account or paid cloud subscription:

```powershell
python serverless/test_local.py
```

---

## 9. Comprehensive Documentation Links

- **System Architecture:** [docs/architecture.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/architecture.md)
- **Module 1 (Virtualization):** [docs/module1-virtualization.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/module1-virtualization.md)
- **Module 2 (VM Automation & KVM):** [docs/module2-automation.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/module2-automation.md)
- **Module 3 (Docker & Docker Hub):** [docs/module3-docker.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/module3-docker.md)
- **Module 4 (Kubernetes & Minikube):** [docs/module4-kubernetes.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/module4-kubernetes.md)
- **Module 5 (AWS Serverless Architecture):** [docs/module5-serverless.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/module5-serverless.md)
- **Full Project Report:** [docs/project_report.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/project_report.md)
- **Viva Questions & Answers:** [docs/viva_questions.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/viva_questions.md)
- **Screenshots Checklist:** [docs/screenshots_checklist.md](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/docs/screenshots_checklist.md)
