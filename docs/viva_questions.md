# ContactHub — 25 College Viva Questions & Answers
## Comprehensive Viva Preparation Guide for BCA Practical Examination

This document provides clear, concise, and technically accurate answers to the most common viva questions asked by external examiners across all 5 syllabus modules and full-stack development.

---

### General Full-Stack & Application Concepts

#### Q1. What is ContactHub, and what is the underlying technology stack?
**Answer:** ContactHub is a secure contact management web application designed to store, organize, search, update, import, and export personal and professional contacts. The technology stack consists of:
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons.
- **Backend:** Python 3 Flask microframework.
- **Database:** SQLite 3 with parameterized queries and indexed fields.
- **Production Server:** Gunicorn WSGI server.
- **DevOps & Cloud:** VirtualBox/KVM (Modules 1 & 2), Docker (Module 3), Kubernetes/Minikube (Module 4), and AWS Lambda/API Gateway (Module 5).

#### Q2. Why did you choose SQLite instead of MySQL or PostgreSQL for the primary application?
**Answer:** SQLite is an embedded, file-based, serverless relational database engine. It requires zero configuration, has no separate server daemon process, stores data in a single portable file, and consumes negligible memory. This makes ContactHub lightweight, fast, and easy to run on student laptops with limited hardware resources while maintaining standard SQL syntax, ACID transactions, and foreign key constraints.

#### Q3. How does ContactHub prevent SQL Injection attacks?
**Answer:** ContactHub strictly avoids string concatenation in SQL queries. Instead, it uses **parameterized queries** with SQLite parameter placeholders (`?`). The SQLite driver ensures user inputs are treated purely as literal data values rather than executable SQL code.

#### Q4. How is user authentication and session security implemented?
**Answer:** Passwords are never stored in plaintext. They are hashed using Werkzeug's secure hashing algorithms (`generate_password_hash` with scrypt/pbkdf2). Authenticated users receive an encrypted HTTP session cookie signed with a server-side secret key (`SECRET_KEY`). Protected routes use a custom `@login_required` decorator that validates the session before allowing access.

#### Q5. How does ContactHub prevent Insecure Direct Object References (IDOR)?
**Answer:** In all contact CRUD routes (view, edit, delete, toggle favorite, export), the backend never queries by contact ID alone. It always appends the authenticated user's ID to the query:
```sql
SELECT * FROM contacts WHERE id = ? AND user_id = ?
```
If User A tries to tamper with the URL to view or delete User B's contact ID, the query returns no record, and the application immediately rejects the request.

---

### Module 1: Introduction to Virtualization

#### Q6. What is virtualization, and what is a Hypervisor?
**Answer:** Virtualization is a technology that allows multiple isolated virtual operating systems (Virtual Machines) to run concurrently on a single physical host machine. The **Hypervisor** (or Virtual Machine Monitor) is the software layer that abstracts physical CPU, RAM, storage, and networking hardware and allocates them to guest virtual machines.

#### Q7. What is the difference between a Type 1 and Type 2 Hypervisor?
**Answer:**
- **Type 1 (Bare-Metal):** Runs directly on the physical hardware without a host operating system (e.g., VMware ESXi, KVM, Microsoft Hyper-V). It offers high performance, low latency, and is used in enterprise cloud data centers.
- **Type 2 (Hosted):** Runs as an application on top of an existing host operating system (e.g., Oracle VirtualBox, VMware Workstation). It is ideal for local software testing and student lab experiments.

#### Q8. What is a Virtual Machine snapshot, and when is it useful?
**Answer:** A snapshot is a point-in-time capture of the virtual machine's complete state, including disk files, system settings, and memory. It is useful as a safety rollback checkpoint before performing risky operations such as OS upgrades or database schema migrations.

#### Q9. What is the difference between a Full Clone and a Linked Clone in VirtualBox?
**Answer:**
- **Full Clone:** An entirely independent duplicate of the parent VM with its own virtual disk. It requires more storage space but remains functional if the parent VM is deleted.
- **Linked Clone:** A lightweight copy that shares base virtual disk blocks with the parent snapshot. It saves disk space but requires the parent snapshot to remain intact.

---

### Module 2: Virtualization Tools & VM Automation

#### Q10. What is KVM, and how does it differ from QEMU?
**Answer:**
- **KVM (Kernel-based Virtual Machine):** A Linux kernel module that turns Linux into a Type-1 hypervisor, allowing guest VMs to execute CPU instructions directly on physical processor cores with hardware virtualization extensions (VT-x/AMD-V).
- **QEMU (Quick Emulator):** Emulates peripheral hardware devices (virtual disks, network interfaces, PCI devices, graphics) that KVM does not handle directly. Together, KVM and QEMU provide complete hardware virtualization.

#### Q11. What is `libvirt` and what is `virsh`?
**Answer:**
- `libvirt` is an open-source library and daemon (`libvirtd`) providing a standardized API for managing different virtualization platforms (KVM, QEMU, Xen, LXC).
- `virsh` is the command-line management tool built on top of `libvirt` used to create, list, pause, start, reboot, and shut down guest virtual machines.

#### Q12. How does the ContactHub script `manage_vm.sh` automate VM tasks?
**Answer:** The script [scripts/manage_vm.sh](file:///C:/Users/ALBIN%20SHIJI/.gemini/antigravity/scratch/ContactHub/scripts/manage_vm.sh) validates user inputs and wraps low-level `virsh` commands into simple operations:
- `manage_vm.sh start <vm>` executes `virsh start <vm>`.
- `manage_vm.sh stop <vm>` executes `virsh shutdown <vm>` for graceful ACPI shutdown.
- `manage_vm.sh list` executes `virsh list --all` to inspect VM states.

---

### Module 3: Containerization Using Docker & Docker Hub

#### Q13. What is the fundamental difference between a Docker Container and a Virtual Machine?
**Answer:** A Virtual Machine packages a full guest operating system kernel along with the application, requiring dedicated RAM, CPU, and gigabytes of storage. A Docker container shares the host operating system's Linux kernel and packages only the application code, runtime, and dependencies, making containers start within seconds and consume a fraction of the memory.

#### Q14. Why is Gunicorn used in the Dockerfile instead of the default Flask development server?
**Answer:** Flask's built-in development server is single-threaded and meant only for local debugging. **Gunicorn** is a production-grade WSGI (Web Server Gateway Interface) server that spawns multiple worker processes (e.g. 4 workers) to handle concurrent HTTP requests reliably without blocking.

#### Q15. Why do we run the Docker container with a non-root user?
**Answer:** Running containers as `root` is a security risk. If an attacker exploits a vulnerability in the application, they could escape the container with root privileges on the host system. In our Dockerfile, we create a dedicated user `contactuser` (UID 1000) with least-privilege permissions.

#### Q16. How does Docker Compose persist SQLite data across container restarts?
**Answer:** Docker containers are ephemeral by default (data written inside a container disappears when the container is deleted). In `docker-compose.yml`, we define a named volume:
```yaml
volumes:
  - contacthub-data:/app/database
```
Docker mounts this volume from host storage into `/app/database`, ensuring the SQLite database file survives container restarts, updates, and rebuilds.

#### Q17. How do you tag and push a Docker image to Docker Hub?
**Answer:**
```powershell
docker login
docker tag contacthub:v1.0 username/contacthub:v1.0
docker push username/contacthub:v1.0
```

---

### Module 4: Container Orchestration with Kubernetes

#### Q18. What is a Kubernetes Pod?
**Answer:** A Pod is the smallest deployable and manageable computing unit in Kubernetes. It encapsulates one or more containers that share identical network namespaces (same IP address and port space) and shared storage volumes.

#### Q19. What is the difference between a Deployment and a ReplicaSet in Kubernetes?
**Answer:**
- A **ReplicaSet** guarantees that a specific number of identical Pod replicas are running at any given time.
- A **Deployment** is a higher-level abstraction that manages ReplicaSets to provide declarative updates, rolling zero-downtime application upgrades, and instant rollbacks.

#### Q20. What is the difference between a ClusterIP and a NodePort Service?
**Answer:**
- **ClusterIP:** The default Kubernetes service type. It assigns an internal cluster IP address accessible only to other pods inside the cluster.
- **NodePort:** Exposes the service on each Kubernetes node's physical IP at a static port (between 30000 and 32767). In ContactHub, port `30080` allows developers to test the application directly in their laptop browser.

#### Q21. What is the difference between Liveness and Readiness probes?
**Answer:**
- **Liveness Probe:** Tests if the application container is healthy and running. If it fails, Kubernetes kills the container and restarts a new one.
- **Readiness Probe:** Tests if the container is ready to accept incoming client traffic. If it fails, Kubernetes stops routing user traffic to that Pod until it passes. Both probes query `/health` in ContactHub.

#### Q22. Can you run 10 replicas of ContactHub on Kubernetes with SQLite? Why or why not?
**Answer:** No. SQLite is a local file-based database that uses file locks. If 10 independent pods write concurrently to the same shared file system or independent storage volumes, data corruption or lock contention occurs. For horizontal scaling across multiple replicas, the application layer must connect to a shared network database such as **PostgreSQL**, **MySQL**, or **Amazon Aurora**.

---

### Module 5: Serverless Architecture (AWS Lambda & API Gateway)

#### Q23. What is Serverless Computing and Function-as-a-Service (FaaS)?
**Answer:** Serverless computing is a cloud execution model where developers write granular code functions without provisioning, configuring, or maintaining servers. Cloud providers automatically run and scale the code on demand. Developers pay only for the exact milliseconds of execution time, and $0 when idle.

#### Q24. How do AWS Lambda and Amazon API Gateway work together in ContactHub?
**Answer:**
1. A client browser or external service sends an HTTP request (e.g. `GET /api/summary`).
2. **Amazon API Gateway** receives the HTTP request and converts it into a structured JSON event payload.
3. API Gateway triggers the **AWS Lambda handler** (`lambda_handler(event, context)`).
4. The Lambda function processes the event, executes the business logic, and returns a response dictionary with HTTP status codes and JSON data.
5. API Gateway translates the Lambda response back to the client.

#### Q25. How does the serverless contact export feature work with Amazon S3?
**Answer:** Generating bulk CSV exports for thousands of contacts can cause high CPU and memory spikes on a monolithic web server. In a serverless architecture, the export request is delegated to a dedicated Lambda function (`contact_export_function.py`). The function generates the CSV file, writes it to an **Amazon S3** bucket, and generates an HMAC-signed **pre-signed URL** expiring in 60 minutes, allowing the user to download the file directly from S3 without burdening the web application.
