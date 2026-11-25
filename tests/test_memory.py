import pytest
from unittest.mock import MagicMock, patch
from src.memory import AgentState
from src.graph import generate_sql_node, generate_answer_node

def test_agent_state_schema():
    """Verify that AgentState schema correctly structures conversational and tool elements."""
    state: AgentState = {
        "user_question": "What is the total revenue?",
        "sql_query": "SELECT SUM(sales_amount) FROM sales_transactions;",
        "query_status": "success",
        "query_results": [{"SUM(sales_amount)": 50000.00}],
        "columns": ["SUM(sales_amount)"],
        "final_answer": "The total sales revenue is $50,000.00.",
        "error_message": None,
        "history": []
    }
    assert state["user_question"] == "What is the total revenue?"
    assert len(state["history"]) == 0

@patch("src.graph.llm_client.generate_response")
def test_generate_answer_node_updates_history(mock_generate_response):
    """Verify that generate_answer_node appends user query and assistant response to history."""
    # Mock the LLM summarization response
    mock_generate_response.return_value = "The total sales revenue is $50,000.00."
    
    # Arrange: Initial state
    state: AgentState = {
        "user_question": "What is the total revenue?",
        "sql_query": "SELECT SUM(sales_amount) FROM sales_transactions;",
        "query_status": "success",
        "query_results": [{"SUM(sales_amount)": 50000.00}],
        "columns": ["SUM(sales_amount)"],
        "final_answer": None,
        "error_message": None,
        "history": []  # Empty initially
    }
    
    # Act: Run node
    result = generate_answer_node(state)
    
    # Assert
    assert result["final_answer"] == "The total sales revenue is $50,000.00."
    assert len(result["history"]) == 2
    assert result["history"][0] == {"role": "user", "content": "What is the total revenue?"}
    assert result["history"][1] == {"role": "assistant", "content": "The total sales revenue is $50,000.00."}

@patch("src.graph.llm_client.generate_response")
def test_generate_sql_node_incorporates_history(mock_generate_response):
    """Verify that generate_sql_node incorporates conversational history to guide the LLM."""
    mock_generate_response.return_value = "SELECT SUM(units_sold) FROM sales_transactions WHERE sales_channel = 'Online';"
    
    # Arrange: State with existing history context (e.g. user previously asked about sales)
    state: AgentState = {
        "user_question": "Now show only the online channel sales.",
        "sql_query": None,
        "query_status": None,
        "query_results": None,
        "columns": None,
        "final_answer": None,
        "error_message": None,
        "history": [
            {"role": "user", "content": "What are our total sales?"},
            {"role": "assistant", "content": "Our total units sold across all transactions is 5,000."}
        ]
    }
    
    # Act: Run node
    result = generate_sql_node(state)
    
    # Assert
    assert "sql_query" in result
    assert "Online" in result["sql_query"]
    
    # Verify the LLM was called, and inspect that history was passed in the user prompt
    called_args, called_kwargs = mock_generate_response.call_args
    user_prompt_passed = called_kwargs.get("user_prompt", called_args[1] if len(called_args) > 1 else "")
    
    assert "What are our total sales?" in user_prompt_passed
    assert "Our total units sold across all transactions" in user_prompt_passed
    assert "Now show only the online channel sales." in user_prompt_passed
