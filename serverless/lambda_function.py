import json
from datetime import datetime, timezone

def lambda_handler(event, context):
    """
    Function A: Contact Summary API (AWS Lambda Handler)
    Triggered via API Gateway HTTP API or direct invocation.
    Generates a secure statistical summary of contact metrics.
    """
    try:
        # Extract HTTP method and query string parameters safely
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        params = event.get('queryStringParameters') or {}
        requested_category = params.get('category', 'all')

        # Fictional summary metrics for serverless demonstration
        summary_payload = {
            "service": "ContactHub",
            "version": "1.0.0",
            "status": "success",
            "message": "Contact summary generated successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": {
                "category": requested_category
            },
            "summary": {
                "total_contacts": 25,
                "personal": 8,
                "work": 10,
                "family": 4,
                "friends": 3,
                "favorites": 6
            },
            "serverless_runtime": {
                "provider": "AWS Lambda",
                "architecture": "x86_64 / arm64",
                "execution_model": "Event-Driven Function-as-a-Service (FaaS)"
            }
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(summary_payload, indent=2)
        }

    except Exception as e:
        error_payload = {
            "service": "ContactHub",
            "status": "error",
            "message": f"Serverless execution error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(error_payload)
        }
