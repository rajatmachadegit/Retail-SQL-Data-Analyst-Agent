from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """The state tracker passed between nodes in the LangGraph StateGraph."""
    user_question: str
    sql_query: Optional[str]
    query_status: Optional[str]       # 'success', 'rejected', 'error'
    query_results: Optional[List[Dict[str, Any]]]
    columns: Optional[List[str]]
    final_answer: Optional[str]
    error_message: Optional[str]
    history: List[Dict[str, str]]