import json
import uuid
from datetime import datetime, timezone

def lambda_handler(event, context):
    """
    Function B: Contact Export Request (AWS Lambda Handler)
    Validates user export request parameters, simulates asynchronous CSV generation,
    and returns a structured response with job metadata and mock S3 pre-signed URI.
    """
    try:
        # Parse incoming body
        body_str = event.get('body')
        payload = {}
        if body_str:
            if isinstance(body_str, str):
                try:
                    payload = json.loads(body_str)
                except json.JSONDecodeError:
                    return {
                        "statusCode": 400,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps({
                            "status": "error",
                            "message": "Malformed JSON in request body"
                        })
                    }
            elif isinstance(body_str, dict):
                payload = body_str

        # Input validation
        user_id = payload.get('user_id')
        export_format = payload.get('format', 'csv').lower()
        category = payload.get('category', 'all')

        if not user_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "error_code": "MISSING_USER_ID",
                    "message": "Authentication error: 'user_id' must be specified in the export request payload."
                })
            }

        if export_format not in ['csv', 'json']:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "error_code": "INVALID_FORMAT",
                    "message": f"Unsupported format '{export_format}'. Allowed formats: 'csv', 'json'."
                })
            }

        # Generate unique Job ID and S3 export path
        job_id = f"export-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        simulated_s3_key = f"exports/user_{user_id}/contacts_{timestamp}.{export_format}"
        presigned_url_mock = f"https://contacthub-export-bucket.s3.amazonaws.com/{simulated_s3_key}?AWSAccessKeyId=MOCK&Expires=3600"

        response_data = {
            "service": "ContactHub",
            "status": "accepted",
            "job_id": job_id,
            "user_id": user_id,
            "export_format": export_format,
            "category_filter": category,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "download_url": presigned_url_mock,
            "expires_in_seconds": 3600,
            "architecture_note": "In a cloud deployment, this Lambda handler queries Amazon DynamoDB / RDS PostgreSQL, writes the CSV to Amazon S3, and signs an S3 GET pre-signed URL for client download."
        }

        return {
            "statusCode": 202,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_data, indent=2)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": f"Serverless execution error: {str(e)}"
            })
        }
