import re

class SQLSafetyGuardrail:
    """Provides validation checks on LLM-generated SQL queries to ensure database safety."""

    # Keywords that are strictly forbidden to prevent database modification or destruction
    FORBIDDEN_KEYWORDS = [
        r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b",
        r"\bALTER\b", r"\bTRUNCATE\b", r"\bCREATE\b", r"\bREPLACE\b",
        r"\bGRANT\b", r"\bREVOKE\b", r"\bEXEC\b", r"\bEXECUTE\b"
    ]

    @classmethod
    def is_query_safe(cls, sql_query: str) -> tuple[bool, str]:
        """
        Validates the SQL query against safety policies.
        Returns:
            (bool, str): (True, "Query is safe") if valid, otherwise (False, descriptive_error_message).
        """
        if not sql_query or not sql_query.strip():
            return False, "SQL query is empty."

        # Clean up whitespace and force uppercase for keyword testing
        clean_query = sql_query.strip().replace("\n", " ").replace("\r", " ")
        upper_query = clean_query.upper()

        # Rule 1: Strictly enforce Read-Only SELECT or WITH (for CTEs) statements
        # A safe query must start with SELECT, SHOW, DESCRIBE, EXPLAIN, or WITH.
        allowed_starts = (r"^SELECT\b", r"^WITH\b", r"^SHOW\b", r"^DESCRIBE\b", r"^EXPLAIN\b")
        starts_safely = any(re.match(pattern, upper_query) for pattern in allowed_starts)

        if not starts_safely:
            return False, "Violation: Query must start with an authorized read-only command (e.g., SELECT or WITH)."

        # Rule 2: Check for forbidden destructive keywords (case-insensitive regex match)
        for pattern in cls.FORBIDDEN_KEYWORDS:
            if re.search(pattern, upper_query):
                keyword = pattern.replace(r"\b", "")
                return False, f"Violation: Query contains forbidden modification keyword '{keyword}'."

        # Rule 3: Prevent Multiple Statements (Semicolon Injection)
        # Clean trailing semicolon, then verify there are no semicolons in the middle of the query
        semicolon_test = clean_query.rstrip(";")
        if ";" in semicolon_test:
            return False, "Violation: Multiple SQL statements or semicolon injections detected."

        return True, "Query is safe."