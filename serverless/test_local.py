"""
Local Test Harness for AWS Lambda Functions (Module 5)
Simulates AWS API Gateway events and Lambda execution environments locally.
"""

import json
import sys
import os

# Add serverless directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lambda_function import lambda_handler as summary_handler
from contact_export_function import lambda_handler as export_handler

def run_tests():
    print("=" * 70)
    print(" ContactHub AWS Lambda Serverless Local Test Runner")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: Function A - Contact Summary (GET)
    # -------------------------------------------------------------
    print("\n[TEST 1] Invoking Function A (Contact Summary Handler)...")
    event_summary = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "category": "Work"
        },
        "requestContext": {
            "http": {"method": "GET"}
        }
    }
    
    response_summary = summary_handler(event_summary, None)
    print(f"Status Code: {response_summary['statusCode']}")
    body_summary = json.loads(response_summary['body'])
    print("Response Body:")
    print(json.dumps(body_summary, indent=2))
    assert response_summary['statusCode'] == 200
    assert body_summary['service'] == "ContactHub"
    assert body_summary['status'] == "success"
    assert body_summary['summary']['total_contacts'] == 25
    print("[PASS] Test 1 completed successfully.")

    # -------------------------------------------------------------
    # TEST 2: Function B - Contact Export Request (Valid POST)
    # -------------------------------------------------------------
    print("\n[TEST 2] Invoking Function B (Valid Export Request)...")
    event_export_valid = {
        "httpMethod": "POST",
        "body": json.dumps({
            "user_id": 1,
            "category": "Work",
            "format": "csv"
        })
    }
    response_export = export_handler(event_export_valid, None)
    print(f"Status Code: {response_export['statusCode']}")
    body_export = json.loads(response_export['body'])
    print("Response Body:")
    print(json.dumps(body_export, indent=2))
    assert response_export['statusCode'] == 202
    assert body_export['status'] == "accepted"
    assert "download_url" in body_export
    assert body_export['user_id'] == 1
    print("[PASS] Test 2 completed successfully.")

    # -------------------------------------------------------------
    # TEST 3: Function B - Validation (Missing User ID)
    # -------------------------------------------------------------
    print("\n[TEST 3] Invoking Function B with Missing user_id (Validation Check)...")
    event_export_invalid = {
        "httpMethod": "POST",
        "body": json.dumps({
            "category": "Work",
            "format": "csv"
        })
    }
    response_invalid = export_handler(event_export_invalid, None)
    print(f"Status Code: {response_invalid['statusCode']}")
    body_invalid = json.loads(response_invalid['body'])
    print("Response Body:", body_invalid)
    assert response_invalid['statusCode'] == 400
    assert body_invalid['error_code'] == "MISSING_USER_ID"
    print("[PASS] Test 3 (Security input validation) passed.")

    # -------------------------------------------------------------
    # TEST 4: Function B - Validation (Invalid Format)
    # -------------------------------------------------------------
    print("\n[TEST 4] Invoking Function B with Unsupported Format...")
    event_format_invalid = {
        "httpMethod": "POST",
        "body": json.dumps({
            "user_id": 1,
            "format": "exe"
        })
    }
    response_format = export_handler(event_format_invalid, None)
    print(f"Status Code: {response_format['statusCode']}")
    body_format = json.loads(response_format['body'])
    print("Response Body:", body_format)
    assert response_format['statusCode'] == 400
    assert body_format['error_code'] == "INVALID_FORMAT"
    print("[PASS] Test 4 (Format validation) passed.")

    print("\n" + "=" * 70)
    print(" ALL SERVERLESS LOCAL TESTS PASSED SUCCESSFULLY! (4/4)")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
