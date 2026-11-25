import mysql.connector
from src.config import MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
from src.safety import SQLSafetyGuardrail

class SQLDatabaseTool:
    """Handles secure execution of validated SQL queries against the MySQL database."""

    @staticmethod
    def get_connection():
        """Creates a fresh connection to the MySQL database."""
        return mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            database=MYSQL_DATABASE,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )

    @classmethod
    def execute_query(cls, sql_query: str) -> dict:
        """
        Validates and runs an SQL query.
        Returns:
            dict: A response dictionary containing execution details, status, and raw results.
        """
        # 1. Run safety check first
        is_safe, message = SQLSafetyGuardrail.is_query_safe(sql_query)
        if not is_safe:
            return {
                "status": "rejected",
                "message": f"Security Guardrail Rejected Query: {message}",
                "columns": [],
                "results": []
            }

        conn = None
        try:
            conn = cls.get_connection()
            # Set dictionary=True to return rows as dictionaries mapped to column headers
            cursor = conn.cursor(dictionary=True)

            cursor.execute(sql_query)

            # Fetch all rows (will be empty if query is SHOW/DESCRIBE with no outputs)
            results = cursor.fetchall()

            # Extract column headers
            columns = cursor.column_names if cursor.column_names else []

            return {
                "status": "success",
                "message": f"Executed successfully. Retrieved {len(results)} rows.",
                "columns": list(columns),
                "results": results
            }

        except mysql.connector.Error as db_err:
            return {
                "status": "error",
                "message": f"Database Execution Error: {db_err}",
                "columns": [],
                "results": []
            }
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()