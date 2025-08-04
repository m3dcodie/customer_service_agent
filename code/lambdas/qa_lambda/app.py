# Import necessary libraries
import json
import traceback
from process_request import process_request 
from domain.libraries.logging_utils import get_logger

# Set up logging
logger = get_logger(__name__)

# Define Lambda function
def lambda_handler(event_body, context):
    # Log the incoming event in JSON format
    logger.info('Event: %s', json.dumps(event_body))

    try:
        if isinstance(event_body, str):
            request_body = json.loads(event_body)
        elif isinstance(event_body, dict):
            request_body = event_body
        else:
            raise ValueError(f"Unsupported event_body type: {type(event_body)}")
        response = process_request(request_body, context)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        stack_trace = traceback.format_exc()
        print(f"stack trace: {stack_trace}")
        print(f"error: {str(e)}")
        response = str(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': response})
        }
    
    return response
    
event = json.dumps({   
    "path": "/check_inventory",
    "parameters": [
        {"name": "ShoeID", "value": "1"},
        {"name": "CustomerID", "value": "1"}
    ],    
    "httpMethod": "POST",    
    "queryStringParameters": None,
    "multiValueQueryStringParameters": None,
    "pathParameters": None,
    "stageVariables": None,   
    "isBase64Encoded": False
}
)

response = lambda_handler(event, None)
print("Response:")
print(response)
