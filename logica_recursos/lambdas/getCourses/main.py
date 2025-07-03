import json

def handler(event, context):
    """
    A simple handler function that returns a static list of courses.
    """
    print("Request received for getCourses")
    
    courses = [
        {"id": "c001", "title": "Introduction to Terraform"},
        {"id": "c002", "title": "Advanced AWS with Python"},
        {"id": "c003", "title": "Serverless Architectures"}
    ]
    
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" # CORS for testing
        },
        "body": json.dumps(courses)
    }
    
    print("Returning response")
    return response
