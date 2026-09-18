import json
import logging
import os
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableClient, UpdateMode

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

TABLE_NAME = "VisitorCounter"
PARTITION_KEY = "visitors"
ROW_KEY = "count"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


@app.route(route="GetResumeCounter", methods=["GET", "POST", "OPTIONS"])
def GetResumeCounter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("[GetResumeCounter] HTTP trigger request received.")

    # 1. Handle browser CORS preflight requests
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers=CORS_HEADERS,
        )

    # 2. Retrieve the Cosmos DB connection string from environment variables
    conn_str = os.environ.get("COSMOS_DB_CONNECTION_STRING")
    if not conn_str:
        logging.error("[GetResumeCounter] Missing COSMOS_DB_CONNECTION_STRING setting.")
        return func.HttpResponse(
            json.dumps({"error": "Database connection string not configured."}),
            status_code=500,
            mimetype="application/json",
            headers=CORS_HEADERS,
        )

    # 3. Connect to the VisitorCounter table, retrieve, increment, and persist count
    try:
        table_client = TableClient.from_connection_string(conn_str=conn_str, table_name=TABLE_NAME)

        try:
            entity = table_client.get_entity(partition_key=PARTITION_KEY, row_key=ROW_KEY)
            current_count = int(entity.get("count", 0))
            new_count = current_count + 1
            entity["count"] = new_count
        except ResourceNotFoundError:
            # Self-healing fallback if initial row was removed or missing
            logging.warning("[GetResumeCounter] Entity not found. Initializing count to 1.")
            new_count = 1
            entity = {
                "PartitionKey": PARTITION_KEY,
                "RowKey": ROW_KEY,
                "count": new_count,
            }

        # Persist updated count to Cosmos DB
        table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity)
        logging.info(f"[GetResumeCounter] Visitor count successfully updated to: {new_count}")

        # 4. Return updated count as JSON response with CORS headers
        response_headers = {
            **CORS_HEADERS,
            "Content-Type": "application/json",
            "Cache-Control": "no-store, no-cache, must-revalidate",
        }

        return func.HttpResponse(
            body=json.dumps({"count": new_count}),
            status_code=200,
            mimetype="application/json",
            headers=response_headers,
        )

    except Exception as e:
        logging.exception(f"[GetResumeCounter] Unexpected error: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Failed to update visitor count", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers=CORS_HEADERS,
        )
