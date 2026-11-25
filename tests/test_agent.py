import pytest
from src.sql_tools import SQLDatabaseTool

def test_db_connection():
    """Verify that the tool can successfully open and close a connection."""
    try:
        conn = SQLDatabaseTool.get_connection()
        assert conn.is_connected() is True
        conn.close()
    except Exception as e:
        pytest.fail(f"Database connection test failed: {e}")

def test_execute_valid_query():
    """Verify that a simple safe query executes and returns data successfully."""
    query = "SELECT COUNT(*) as store_count FROM stores;"
    result = SQLDatabaseTool.execute_query(query)

    assert result["status"] == "success"
    assert "store_count" in result["columns"]
    assert len(result["results"]) == 1
    assert result["results"][0]["store_count"] > 0