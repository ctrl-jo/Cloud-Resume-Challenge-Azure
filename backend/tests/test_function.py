"""
Unit tests for GetResumeCounter Azure Function (Step 11).

Tests run entirely offline using unittest.mock — no live Cosmos DB calls.
Covers: happy path increment, self-healing initialization, missing connection
string, CORS preflight, and unexpected database errors.
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import UpdateMode

# Import the function under test
from function_app import GetResumeCounter


# ---------------------------------------------------------------------------
# Helper: Build a mock HttpRequest
# ---------------------------------------------------------------------------
def _build_request(method: str = "GET", url: str = "/api/GetResumeCounter") -> func.HttpRequest:
    """Construct a minimal mock HttpRequest for testing."""
    return func.HttpRequest(
        method=method,
        url=url,
        headers={},
        params={},
        body=b"",
    )


# ===========================================================================
# Test Suite
# ===========================================================================
class TestGetResumeCounter(unittest.TestCase):
    """Unit tests for the GetResumeCounter HTTP-triggered Azure Function."""

    # -----------------------------------------------------------------------
    # 1. Happy Path — Entity exists, count increments from N to N+1
    # -----------------------------------------------------------------------
    @patch("function_app.TableClient")
    @patch.dict(os.environ, {"COSMOS_DB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=dGVzdA==;TableEndpoint=https://test.table.cosmos.azure.com:443/;"})
    def test_happy_path_increments_count(self, mock_table_class):
        """When entity exists with count=5, function returns count=6 and upserts."""
        # Arrange
        mock_client = MagicMock()
        mock_table_class.from_connection_string.return_value = mock_client

        # Simulate existing entity with count = 5
        mock_client.get_entity.return_value = {
            "PartitionKey": "visitors",
            "RowKey": "count",
            "count": 5,
        }

        req = _build_request("GET")

        # Act
        response = GetResumeCounter(req)

        # Assert — HTTP response
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.get_body())
        self.assertEqual(body["count"], 6)

        # Assert — upsert was called with incremented entity
        mock_client.upsert_entity.assert_called_once()
        upserted_entity = mock_client.upsert_entity.call_args
        self.assertEqual(upserted_entity.kwargs["entity"]["count"], 6)
        self.assertEqual(upserted_entity.kwargs["mode"], UpdateMode.REPLACE)

    # -----------------------------------------------------------------------
    # 2. Initialization Path — Entity missing, self-heals with count=1
    # -----------------------------------------------------------------------
    @patch("function_app.TableClient")
    @patch.dict(os.environ, {"COSMOS_DB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=dGVzdA==;TableEndpoint=https://test.table.cosmos.azure.com:443/;"})
    def test_initialization_creates_entity_on_not_found(self, mock_table_class):
        """When entity does not exist, function creates it with count=1."""
        # Arrange
        mock_client = MagicMock()
        mock_table_class.from_connection_string.return_value = mock_client

        # Simulate ResourceNotFoundError on get_entity
        mock_client.get_entity.side_effect = ResourceNotFoundError("Entity not found")

        req = _build_request("GET")

        # Act
        response = GetResumeCounter(req)

        # Assert — HTTP response
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.get_body())
        self.assertEqual(body["count"], 1)

        # Assert — upsert was called with a fresh entity
        mock_client.upsert_entity.assert_called_once()
        upserted_entity = mock_client.upsert_entity.call_args.kwargs["entity"]
        self.assertEqual(upserted_entity["PartitionKey"], "visitors")
        self.assertEqual(upserted_entity["RowKey"], "count")
        self.assertEqual(upserted_entity["count"], 1)

    # -----------------------------------------------------------------------
    # 3. Missing Connection String — Returns 500
    # -----------------------------------------------------------------------
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_connection_string_returns_500(self):
        """When COSMOS_DB_CONNECTION_STRING is not set, function returns 500."""
        req = _build_request("GET")

        # Act
        response = GetResumeCounter(req)

        # Assert
        self.assertEqual(response.status_code, 500)
        body = json.loads(response.get_body())
        self.assertIn("error", body)
        self.assertIn("connection string", body["error"].lower())

    # -----------------------------------------------------------------------
    # 4. CORS Preflight — OPTIONS returns 204 with correct headers
    # -----------------------------------------------------------------------
    def test_options_returns_cors_preflight(self):
        """OPTIONS request returns 204 with CORS headers, no DB interaction."""
        req = _build_request("OPTIONS")

        # Act
        response = GetResumeCounter(req)

        # Assert
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response.headers["Access-Control-Allow-Methods"], "GET, POST, OPTIONS")
        self.assertEqual(response.headers["Access-Control-Allow-Headers"], "Content-Type")

    # -----------------------------------------------------------------------
    # 5. Database Exception — Unexpected error returns 500
    # -----------------------------------------------------------------------
    @patch("function_app.TableClient")
    @patch.dict(os.environ, {"COSMOS_DB_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=dGVzdA==;TableEndpoint=https://test.table.cosmos.azure.com:443/;"})
    def test_unexpected_db_error_returns_500(self, mock_table_class):
        """When an unexpected exception occurs, function returns 500 with error details."""
        # Arrange
        mock_client = MagicMock()
        mock_table_class.from_connection_string.return_value = mock_client

        # Simulate an unexpected database error
        mock_client.get_entity.side_effect = Exception("Connection timeout")

        req = _build_request("GET")

        # Act
        response = GetResumeCounter(req)

        # Assert
        self.assertEqual(response.status_code, 500)
        body = json.loads(response.get_body())
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Failed to update visitor count")
        self.assertIn("Connection timeout", body["details"])


if __name__ == "__main__":
    unittest.main()
