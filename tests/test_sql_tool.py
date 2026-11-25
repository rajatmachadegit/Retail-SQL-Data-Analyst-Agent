import pytest
from unittest.mock import MagicMock, patch
import mysql.connector
from src.sql_tools import SQLDatabaseTool

@patch("src.sql_tools.SQLDatabaseTool.get_connection")
def test_execute_query_safe_success(mock_get_connection):
    """Verify successful execution of a safe query using mocked database components."""
    # Setup mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Configure mock return data
    mock_cursor.column_names = ["product_name", "category"]
    mock_cursor.fetchall.return_value = [
        {"product_name": "Premium Beans", "category": "Coffee"},
        {"product_name": "Organic Milk", "category": "Dairy"}
    ]
    
    # Execute tool
    query = "SELECT product_name, category FROM products;"
    result = SQLDatabaseTool.execute_query(query)
    
    # Assertions
    assert result["status"] == "success"
    assert "Executed successfully" in result["message"]
    assert result["columns"] == ["product_name", "category"]
    assert len(result["results"]) == 2
    assert result["results"][0]["product_name"] == "Premium Beans"
    
    # Verify DB methods were called correctly
    mock_cursor.execute.assert_called_once_with(query)
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

def test_execute_query_guardrail_rejected():
    """Verify that execute_query instantly rejects and bypasses DB connection for blocked queries."""
    query = "DROP TABLE products;"
    result = SQLDatabaseTool.execute_query(query)
    
    assert result["status"] == "rejected"
    assert "Security Guardrail Rejected Query" in result["message"]
    assert result["results"] == []
    assert result["columns"] == []

@patch("src.sql_tools.SQLDatabaseTool.get_connection")
def test_execute_query_database_error(mock_get_connection):
    """Verify how SQLDatabaseTool handles a driver-level database execution exception."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Force cursor.execute to raise a mysql connector Error
    mock_cursor.execute.side_effect = mysql.connector.Error(
        msg="Table 'retail_agent_assignment.wrong_table' doesn't exist",
        errno=1146
    )
    
    query = "SELECT * FROM wrong_table;"
    result = SQLDatabaseTool.execute_query(query)
    
    assert result["status"] == "error"
    assert "Database Execution Error" in result["message"]
    assert "1146" in result["message"] or "wrong_table" in result["message"]
    assert result["results"] == []
    
    # Ensure connections are closed during exception handling
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
