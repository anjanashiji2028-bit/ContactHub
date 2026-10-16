# ContactHub — Project Report & Documentation
## Bachelor of Computer Applications (BCA) Microproject

---

## 1. Abstract

**ContactHub** is a secure, responsive, and lightweight web application engineered to store, manage, categorize, search, import, and export personal and professional contacts. Beyond standard CRUD operations, ContactHub is architected to comprehensively fulfill the academic practical requirements of all five syllabus modules of modern cloud computing and DevOps:
1. Virtualization
2. Virtualization Tools & VM Automation
3. Containerization using Docker & Docker Hub
4. Container Orchestration using Kubernetes & Minikube
5. Serverless Architecture using AWS Lambda & Amazon API Gateway

Built using Python Flask, SQLite, Bootstrap 5, and Gunicorn, the project balances academic rigor with minimal hardware overhead, allowing smooth execution on standard student laptops running Windows.

---

## 2. Problem Statement

Modern professionals and students maintain contacts scattered across fragmented mobile devices, email inboxes, spreadsheets, and social channels. Existing commercial solutions either impose vendor lock-in, demand costly enterprise subscriptions, or pose privacy concerns by monetizing user address book data. Furthermore, from an educational standpoint, computer applications students frequently struggle to bridge the gap between monolithic application development and real-world DevOps practices (virtualization, containerization, orchestration, and serverless architectures).

**ContactHub** solves both challenges by offering a self-hosted, privacy-respecting contact management platform and providing an end-to-end practical demonstration of modern deployment engineering.

---

## 3. Objectives

1. Develop a secure, responsive full-stack contact management application with strict user privacy and zero data leakage.
2. Provide intuitive search, categorization, favorite tagging, and CSV bulk import/export workflows with duplicate detection.
3. Demonstrate bare-metal and hosted virtualization workflows in Type-1 (KVM) and Type-2 (VirtualBox) hypervisors.
4. Automate virtual machine lifecycle management using Linux shell scripts and `virsh`.
5. Package the application into a hardened, non-root Docker container with persistent SQLite volume storage and automated healthchecks.
6. Deploy and orchestrate the containerized application on a Kubernetes cluster with self-healing, rolling updates, and service discovery.
7. Implement an event-driven serverless architecture using AWS Lambda and API Gateway for decoupled reporting and export operations.
8. Implement 100% automated test coverage with pytest.

---

## 4. Scope & Boundaries

### Included Functionality
- User authentication with Werkzeug password hashing and session cookies.
- Multi-field contact search (name, email, phone, company, city).
- Contact categorization (Personal, Work, Family, Friends, Other).
- CSV export restricted to the logged-in user.
- CSV import with duplicate detection handling (`skip`, `update`, `allow_duplicates`).
- Real-time `/health` system monitor endpoint.
- Complete Dockerfile, Docker Compose, Kubernetes manifests, and AWS SAM templates.
- Automated PowerShell and Bash administration scripts.

### Excluded / Non-Goals
- Paid third-party SMS or transactional email dispatchers (to keep execution completely free and lightweight).
- Public contact sharing (to preserve privacy and security).

---

## 5. Requirements Specification

### Functional Requirements
- **FR1 (Authentication):** Users must be able to register, log in, view account profile, update password, and securely log out.
- **FR2 (Contact CRUD):** Users must be able to create, read, update, and delete contacts with confirmation dialogues.
- **FR3 (Data Isolation):** Users must strictly access only their own contacts. Cross-user access via IDOR must be blocked.
- **FR4 (Search & Filter):** Contacts must be filterable by keyword, category, favorite status, and alphabetical/date sorting.
- **FR5 (Import & Export):** Users must be able to export contacts to standard CSV format and import contacts with duplicate handling.
- **FR6 (Health Monitoring):** System must expose a `/health` endpoint returning JSON service and database connectivity status.

### Non-Functional Requirements
- **NFR1 (Security):** Parameterized SQL queries, CSRF token validation, session encryption, and non-root container execution.
- **NFR2 (Performance):** Page render times under 100ms; sub-second search using database indexes.
- **NFR3 (Portability):** Runs identically on bare-metal Windows, Linux VMs, Docker containers, and Kubernetes pods.
- **NFR4 (Storage Efficiency):** Entire application and database footprint occupies under 50MB of disk storage.

---

## 6. Hardware & Software Requirements

### Hardware Requirements
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher.
- **Memory (RAM):** Minimum 4 GB RAM (8 GB recommended for running Minikube or Docker Desktop).
- **Storage:** 1 GB free hard drive space.

### Software Requirements
- **Operating System:** Windows 10/11, Ubuntu 22.04 LTS+, or macOS.
- **Programming Language:** Python 3.10+ (tested on Python 3.14).
- **Database Engine:** SQLite 3.
- **Container Engine:** Docker Desktop / Docker Engine.
- **Orchestration Tool:** Minikube & kubectl.
- **Web Browser:** Google Chrome, Mozilla Firefox, or Microsoft Edge.

---

## 7. Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript | Lightweight, zero node_modules overhead |
| **CSS Framework** | Bootstrap 5.3 + Bootstrap Icons | Modern, mobile-responsive layout and typography |
| **Backend Framework** | Python 3 Flask | Minimalist, highly readable microframework |
| **Database** | SQLite 3 | Embedded, zero-configuration relational database |
| **Production WSGI** | Gunicorn | Production-grade WSGI HTTP server |
| **Container Engine** | Docker & Docker Compose | Container encapsulation and persistent volumes |
| **Container Orchestration**| Kubernetes & Minikube | Pod replication, service discovery, rolling updates |
| **Serverless Compute** | AWS Lambda & API Gateway | Serverless event-driven execution (Module 5) |
| **Testing** | pytest | Automated unit, integration, and security testing |

---

## 8. Database Design

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts Table
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    secondary_phone TEXT,
    email TEXT,
    company TEXT,
    job_title TEXT,
    address TEXT,
    city TEXT,
    category TEXT NOT NULL DEFAULT 'Other',
    notes TEXT,
    is_favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for Fast Query Performance
CREATE INDEX idx_contacts_user_id ON contacts(user_id);
CREATE INDEX idx_contacts_full_name ON contacts(full_name);
CREATE INDEX idx_contacts_category ON contacts(category);
CREATE INDEX idx_contacts_is_favorite ON contacts(is_favorite);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_phone ON contacts(phone);
```

---

## 9. Actual Test Results & Verification

All automated test suites were executed directly in the project environment and achieved 100% pass rates:

### A. Application Test Suite (pytest)
```
platform win32 -- Python 3.14.7, pytest-9.1.1
collected 23 items

tests/test_auth.py::test_registration_success PASSED                     [  4%]
tests/test_auth.py::test_registration_duplicate_email PASSED             [  8%]
tests/test_auth.py::test_registration_password_mismatch PASSED           [ 13%]
tests/test_auth.py::test_registration_short_password PASSED              [ 17%]
tests/test_auth.py::test_login_success PASSED                            [ 21%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 26%]
tests/test_auth.py::test_protected_route_requires_login PASSED           [ 30%]
tests/test_auth.py::test_logout PASSED                                   [ 34%]
tests/test_contacts.py::test_create_contact_success PASSED               [ 39%]
tests/test_contacts.py::test_create_contact_validation_failure PASSED    [ 43%]
tests/test_contacts.py::test_edit_contact PASSED                         [ 47%]
tests/test_contacts.py::test_delete_contact PASSED                       [ 52%]
tests/test_contacts.py::test_toggle_favorite PASSED                      [ 56%]
tests/test_contacts.py::test_search_and_filter PASSED                    [ 60%]
tests/test_contacts.py::test_strict_user_isolation PASSED                [ 65%]
tests/test_health.py::test_health_endpoint_healthy PASSED                [ 69%]
tests/test_health.py::test_homepage_loads PASSED                         [ 73%]
tests/test_import_export.py::test_export_csv PASSED                      [ 78%]
tests/test_import_export.py::test_export_isolation PASSED                [ 82%]
tests/test_import_export.py::test_import_template_download PASSED        [ 86%]
tests/test_import_export.py::test_import_csv_valid_data PASSED           [ 91%]
tests/test_import_export.py::test_import_csv_duplicate_skip PASSED       [ 95%]
tests/test_import_export.py::test_import_csv_missing_required_columns PASSED [100%]

============================= 23 passed in 16.46s =============================
```

### B. Serverless Test Suite (`serverless/test_local.py`)
```
[TEST 1] Invoking Function A (Contact Summary Handler)...
Status Code: 200 OK -> [PASS] Test 1 completed successfully.

[TEST 2] Invoking Function B (Valid Export Request)...
Status Code: 202 Accepted -> [PASS] Test 2 completed successfully.

[TEST 3] Invoking Function B with Missing user_id (Validation Check)...
Status Code: 400 Bad Request (MISSING_USER_ID) -> [PASS] Test 3 passed.

[TEST 4] Invoking Function B with Unsupported Format...
Status Code: 400 Bad Request (INVALID_FORMAT) -> [PASS] Test 4 passed.

ALL SERVERLESS LOCAL TESTS PASSED SUCCESSFULLY! (4/4)
```

---

## 10. Limitations

1. **SQLite Concurrency Limitation:** SQLite relies on database-level file locks for write transactions. While ideal for single-replica local deployments, multiple active write instances across multi-pod Kubernetes clusters require a network database like PostgreSQL.
2. **Local Session Storage:** Flask client-side cookie sessions are used. High-volume horizontal scaling requires distributed session stores like Redis.

---

## 11. Future Enhancements

1. **PostgreSQL Migration:** Add a configuration flag allowing one-click migration from SQLite to AWS RDS PostgreSQL or Dockerized Postgres.
2. **Contact vCard (.vcf) Support:** Support importing and exporting contacts using the universal `.vcf` format for direct sync with smartphones.
3. **Multi-Factor Authentication (MFA):** Integrate TOTP (Google Authenticator) for two-factor login security.
4. **Automated CI/CD Pipeline:** Add GitHub Actions workflows to automate Docker image builds and deployment to Kubernetes upon git push.

---

## 12. Conclusion

The **ContactHub — Contact Management System** successfully achieves all project goals. It delivers a fast, secure, user-friendly contact management application while serving as a comprehensive educational bridge across all five core syllabus modules: Virtualization, VM Automation, Docker Containerization, Kubernetes Orchestration, and AWS Serverless Architecture.
