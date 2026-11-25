import sys
from src.graph import agent_graph

def run_cli_app():
    """Runs an interactive command-line interface for the Retail SQL Analyst Agent."""
    print("=" * 60)
    print("      RETAIL SQL DATA ANALYST AGENT - INTERACTIVE CLI")
    print("=" * 60)
    print("Type your retail business questions in plain English.")
    print("The agent will automatically translate them to SQL, query the database,")
    print("and summarize the results. Conversation history is saved for follow-ups.")
    print("-" * 60)
    print("Type 'exit' or 'quit' to close the application.")
    print("=" * 60)

    # Initialize the conversational state
    state = {
        "user_question": "",
        "sql_query": None,
        "query_status": None,
        "query_results": None,
        "columns": None,
        "final_answer": None,
        "error_message": None,
        "history": [] # Memory persistency
    }

    while True:
        try:
            print("\n" + "_" * 50)
            user_input = input("\nUser 👤: ").strip()

            # Check for termination command
            if user_input.lower() in ["exit", "quit"]:
                print("\nThank you for using the Retail SQL Analyst Agent. Goodbye!")
                break

            if not user_input:
                print("Warning: Input is empty. Please enter a question.")
                continue

            # Update the state with the new user question
            state["user_question"] = user_input

            # Reset intermediate variables for the new run
            state["sql_query"] = None
            state["query_status"] = None
            state["query_results"] = None
            state["columns"] = None
            state["final_answer"] = None
            state["error_message"] = None

            # Execute the compiled LangGraph StateGraph pipeline
            print("Processing your question... ⚙️")
            updated_state = agent_graph.invoke(state)

            # Retrieve processed information
            sql_query = updated_state.get("sql_query", "No Query Generated")
            status = updated_state.get("query_status", "unknown")
            final_answer = updated_state.get("final_answer", "No Answer Generated")
            error_msg = updated_state.get("error_message")

            # Display Developer Output (Human-in-the-Loop review)
            print("-" * 50)
            print(f"Generated SQL Query:  {sql_query}")
            print(f"Database Query Status: {status.upper()}")

            if status == "error" and error_msg:
                print(f"Database Error:        {error_msg}")
            elif status == "rejected" and error_msg:
                print(f"Security Guardrail:    {error_msg}")
            print("-" * 50)

            # Display Final Agent Output
            print(f"\nAgent 🤖: {final_answer}")

            # Feed the updated state (and running conversation history) back into memory
            state = updated_state

        except KeyboardInterrupt:
            print("\n\nApplication interrupted. Closing connection. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n[System Error]: An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_cli_app()