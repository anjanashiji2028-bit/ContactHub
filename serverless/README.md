# ContactHub Serverless Architecture Guide (Module 5)

This directory demonstrates the **Serverless Architecture** module of the BCA Cloud Computing curriculum using **AWS Lambda**, **Amazon API Gateway (HTTP API)**, **Amazon S3**, and **AWS SAM (Serverless Application Model)**.

---

## 1. Key Concepts

### What is Serverless Computing?
Serverless is a cloud execution model where cloud providers automatically provision, scale, and manage infrastructure required to run code. Developers pay only for the exact execution duration (measured in milliseconds) rather than paying for idle virtual machines or always-running servers.

### Function-as-a-Service (FaaS)
FaaS enables developers to execute modular business logic in response to events without deploying an entire application server stack.

### Event-Driven Architecture
AWS Lambda functions are invoked by events:
- **Synchronous HTTP Events:** API Gateway receives an HTTP request and invokes Lambda, returning the HTTP response.
- **Asynchronous Events:** File uploads to Amazon S3, messages in Amazon SQS, or scheduled Amazon EventBridge cron jobs trigger background processing.

---

## 2. Serverless Component Breakdown

| File | Purpose | Cloud Resource |
| :--- | :--- | :--- |
| `lambda_function.py` | Function A: Contact summary metrics API | AWS Lambda + API Gateway (GET) |
| `contact_export_function.py` | Function B: Validates export request & generates pre-signed S3 link | AWS Lambda + API Gateway (POST) |
| `template.yaml` | Infrastructure as Code (IaC) SAM template | API Gateway, Lambda, IAM, S3 Bucket |
| `test_local.py` | Zero-dependency local test harness simulating API Gateway events | Local Python Runtime |

---

## 3. Local Testing (No AWS Account Required)

You do **not** need an AWS account or paid cloud subscription to test and verify these serverless functions on your local machine.

Run the local test harness from Windows PowerShell:

```powershell
python serverless/test_local.py
```

### Expected Output
The test runner executes 4 distinct event simulations:
1. `GET` request to Function A returning status `200 OK` with JSON contact metrics.
2. `POST` request to Function B with valid JSON payload returning status `202 Accepted` with a signed S3 URI.
3. `POST` request with missing `user_id` returning `400 Bad Request` with `MISSING_USER_ID` error.
4. `POST` request with unsupported file format returning `400 Bad Request` with `INVALID_FORMAT` error.

---

## 4. Cloud Deployment with AWS SAM (Optional Practical)

If you have an active AWS account, follow these steps to deploy into the cloud.

### Prerequisites
1. **AWS CLI** installed:
   ```powershell
   aws --version
   ```
2. **AWS Credentials** configured:
   ```powershell
   aws configure
   ```
   *(Enter your AWS Access Key, Secret Key, and preferred region e.g. `ap-south-1` for Mumbai).*
3. **AWS SAM CLI** installed:
   ```powershell
   sam --version
   ```

### Deployment Commands

```powershell
# 1. Navigate to the serverless folder
cd serverless

# 2. Build the SAM application
sam build

# 3. Deploy guided stack (prompts for Stack Name, Region, Confirm changes)
sam deploy --guided
```

Once deployment completes, SAM outputs the live API Gateway URLs:
```
SummaryApiEndpoint: https://xyz123.execute-api.ap-south-1.amazonaws.com/api/summary
ExportApiEndpoint:  https://xyz123.execute-api.ap-south-1.amazonaws.com/api/export
```

### Test Live Cloud Endpoints with cURL or PowerShell

```powershell
# Test Summary API
curl.exe https://xyz123.execute-api.ap-south-1.amazonaws.com/api/summary

# Test Export Request API
curl.exe -X POST https://xyz123.execute-api.ap-south-1.amazonaws.com/api/export `
  -H "Content-Type: application/json" `
  -d '{"user_id": 1, "format": "csv", "category": "Work"}'
```

---

## 5. Security & Least Privilege Permissions

1. **IAM Roles:** The Lambda execution role follows the principle of least privilege, allowing read/write access strictly to the dedicated `ContactExportBucket` S3 bucket.
2. **Input Sanitization:** Both handlers validate parameters and reject unexpected payloads before downstream processing.
3. **S3 Public Access Block:** The export S3 bucket explicitly blocks all public access (`BlockPublicAcls: true`). Files can only be downloaded via short-lived pre-signed URLs expiring in 60 minutes.
4. **Lifecycle Expiration:** S3 automatically purges temporary export files after 7 days, eliminating cloud storage waste.

---

## 6. Teardown / Cleanup Commands

To delete all serverless cloud resources and avoid incurring any AWS charges:

```powershell
sam delete --stack-name contacthub-serverless
```
