from botocore.exceptions import ClientError
from domain.libraries.logging_utils import get_logger
from handlers.tool_agent_handler import ToolAgentHandler

# Set up logging
logger = get_logger(__name__)

def process_request(request_body, context):
    """Process the incoming request and dispatch to the appropriate handler."""
    # Check for Bedrock agent event
    handler = ToolAgentHandler()
  
    try:
        return handler.handle(request_body, context)
    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error("A client error occurred: %s", message)
        print(f"A client error occured: {message}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        print(f"An unexpected error occurred: {str(e)}")
   
