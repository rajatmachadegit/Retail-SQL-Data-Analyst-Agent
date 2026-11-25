import pytest
from src.safety import SQLSafetyGuardrail

def test_safe_select_query():
    """Verify that a standard read-only SELECT query is accepted by the guardrail."""
    query = "SELECT product_name, category FROM products WHERE base_price > 50;"
    is_safe, message = SQLSafetyGuardrail.is_query_safe(query)
    assert is_safe is True
    assert "safe" in message.lower()

def test_safe_with_query():
    """Verify that Common Table Expressions (CTEs) starting with WITH are accepted."""
    query = "WITH high_sales AS (SELECT * FROM sales_transactions WHERE units_sold > 5) SELECT * FROM high_sales;"
    is_safe, message = SQLSafetyGuardrail.is_query_safe(query)
    assert is_safe is True

def test_blocks_drop_table():
    """Verify that a DROP TABLE command is blocked."""
    query = "DROP TABLE stores;"
    is_safe, message = SQLSafetyGuardrail.is_query_safe(query)
    assert is_safe is False
    assert "Violation" in message

def test_blocks_delete_records():
    """Verify that DELETE commands are blocked."""
    query = "DELETE FROM customers WHERE customer_id = 'C001';"
    is_safe, message = SQLSafetyGuardrail.is_query_safe(query)
    assert is_safe is False
    assert "Violation" in message

def test_blocks_semicolon_injection():
    """Verify that multiple statements separated by semicolons are blocked."""
    # Updated query to only use safe SELECTs to isolate the semicolon validation
    query = "SELECT * FROM products; SELECT * FROM customers;"
    is_safe, message = SQLSafetyGuardrail.is_query_safe(query)
    assert is_safe is False
    assert "semicolon" in message.lower()