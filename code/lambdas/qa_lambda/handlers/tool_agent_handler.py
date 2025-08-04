import boto3
import json
import os
import sqlite3
from datetime import datetime
from domain.libraries.logging_utils import get_logger

logger = get_logger(__name__)

class ToolAgentHandler:
    def __init__(self):
        self.s3 = boto3.client("s3")
        self.bucket = os.environ.get("ARTIFACT_BUCKET")
        self.db_name = "tool_agent/demo_csbot_db"
        self.local_db = "/tmp/csbot.db"
        self.conn = None
        self.cursor = None
        self._ensure_db_loaded()

    def _ensure_db_loaded(self):
        # Download the database file from S3 to the local /tmp folder
        if not os.path.exists(self.local_db):
            self.s3.download_file(self.bucket, self.db_name, self.local_db)
        self.conn = sqlite3.connect(self.local_db)
        self.cursor = self.conn.cursor()
        logger.info("Completed initial data load")

    def return_customer_info(self, custName):
        query = "SELECT customerId, customerName, Addr1, Addr2, City, State, Zipcode, PreferredActivity, ShoeSize, OtherInfo FROM CustomerInfo WHERE customerName LIKE ?"
        self.cursor.execute(query, ("%" + custName + "%",))
        resp = self.cursor.fetchall()
        if resp:
            names = [description[0] for description in self.cursor.description]
            valDict = {names[i]: resp[0][i] for i in range(len(names))}
            logger.info("Customer info retrieved")
            return valDict
        else:
            logger.info("Customer not found")
            return {}

    def return_shoe_inventory(self):
        query = "SELECT customerId, customerName, Addr1, Addr2, City, State, Zipcode, PreferredActivity, ShoeSize, OtherInfo FROM CustomerInfo"
        self.cursor.execute(query)
        resp = self.cursor.fetchall()
        print(resp)
        names = [description[0] for description in self.cursor.description]
        valDict = [{names[i]: item[i] for i in range(len(names))} for item in resp]
        logger.info("Shoe inventory retrieved")
        return valDict

    def place_shoe_order(self, ssId, custId):
        try:
            query = "UPDATE ShoeInventory SET InvCount = InvCount - 1 WHERE ShoeID = ?"
            self.cursor.execute(query, (ssId,))
            today = datetime.today().strftime("%Y-%m-%d")
            query = (
                "INSERT INTO OrderDetails (orderdate, shoeId, CustomerId) VALUES (?, ?, ?)"
            )
            self.cursor.execute(query, (today, ssId, custId))
            self.conn.commit()
            self.s3.upload_file(self.local_db, self.bucket, self.db_name)
            logger.info("Shoe order placed")
            return 1
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return 0

    def handle(self, event, context):
        # event is the request_body from process_request
        api_path = event.get("apiPath") or event.get("path")
        logger.info(f"API Path: {api_path}")
        parameters = event.get("parameters", [])
        body = {}
        if api_path == "/customer/{CustomerName}":
            custName = next((param["value"] for param in parameters if param["name"] == "CustomerName"), "")
            body = self.return_customer_info(custName)
        elif api_path == "/place_order":
            ssId = next((param["value"] for param in parameters if param["name"] == "ShoeID"), "")
            custId = next((param["value"] for param in parameters if param["name"] == "CustomerID"), "")
            body = self.place_shoe_order(ssId, custId)
        elif api_path == "/check_inventory":
            body = self.return_shoe_inventory()
        else:
            body = {"message": f"{api_path} is not a valid API, try another one."}
        response_body = {"application/json": {"body": json.dumps(body)}}
        action_response = {
            "actionGroup": event.get("actionGroup"),
            "apiPath": api_path,
            "httpMethod": event.get("httpMethod"),
            "httpStatusCode": 200,
            "responseBody": response_body,
        }
        api_response = {"messageVersion": "1.0", "response": action_response}
        return api_response
