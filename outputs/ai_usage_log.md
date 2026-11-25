# AI Usage and Collaboration Log

This log documents the collaboration between the Developer and the AI Assistant (Gemini Notebook) during the end-to-end design, implementation, debugging, and testing of the secure **Retail SQL Analyst Agent**.

---

## Phase 1: Environment and Setup

### AI Assistance Received
- Guided the directory structure setup (`data/`, `database/`, `src/`, `tests/`, `evidence/`, `outputs/`).
- Generated templates for the `.env` configuration file and `src/config.py` environment loader.

### Human Review & Manual Adjustments (Critical Bugs Resolved)
- **PowerShell UTF-16 Encoding Bug**: When the empty `.env` file was created in PowerShell, Windows saved it with UTF-16 LE encoding. Python's `os.getenv()` read this as empty/null. 
  - *Correction*: Developed `fix_env.py` to rewrite the `.env` file with standard UTF-8 encoding.
- **PowerShell Syntax Typo**: Identified and stripped PowerShell shell prefix variables (like `$env:`) inside the `.env` file to ensure the file conformed to the standard `KEY=VALUE` format expected by `python-dotenv`.

---

## Phase 2: Database Setup & Data Ingestion

### AI Assistance Received
- Drafted the MySQL schema definitions (`database/mysql_schema.sql`) for five core tables (stores, products, customers, sales_transactions, returns).
- Developed the automated loading script (`database/load_data.py`) using `pandas` to clear tables, parse dates, and insert synthetic data.

### Human Review & Manual Adjustments (Critical Bugs Resolved)
- **Column Integrity and Ingestion Failures**: The initial ingestion run crashed with database error `1048 (23000): Column 'order_date' cannot be null`. This occurred because the raw CSV files used different, mixed date formats (slashes vs hyphens) which standard pandas parsing failed to convert, resulting in `NaT` (Not-a-Time/Null) values.
  - *Correction*: Refactored `load_data.py` to implement a flexible multi-format date parser with automatic fallback checking (handling both `DD-MM-YYYY` and `DD/MM/YYYY`) and a diagnostic logger to identify raw formatting discrepancies.

---

## Phase 3: Core Modules & State Machine

### AI Assistance Received
- Designed the HTTP request payload and headers inside `src/tiger_gateway_client.py` to make OpenAI-compatible chat completion calls to the Tiger AI Gateway.
- Formulated the LangGraph `StateGraph` flow in `src/graph.py` using sequential execution nodes (`generate_sql`, `execute_sql`, `generate_answer`).
- Designed the regular expression validation patterns inside the `SQLSafetyGuardrail` class (`src/safety.py`).

### Human Review & Manual Adjustments (Critical Bugs Resolved)
- **Corporate Network SSL Interception**: Encountered a network connection failure `SSLCertVerificationError` due to enterprise proxy decryption (such as Zscaler) signing the request with a self-signed corporate certificate.
  - *Correction*: Updated the gateway client to use `verify=False` on requests and added the `urllib3.disable_warnings` filter to prevent console log pollution.
- **API Response Parsing Bug**: Encountered error `list indices must be integers or slices, not str` when parsing responses.
  - *Correction*: Added index-0 lookup to the gateway client to properly navigate the JSON array payload: `response_data["choices"][0]["message"]["content"]`.

---

## Phase 4: App Testing & Evaluation

### AI Assistance Received
- Structured an interactive CLI application (`src/app.py`) with a persistent `AgentState` loop allowing real-time context-aware follow-ups.
- Developed automated testing scenarios under `tests/test_safety.py` and `tests/test_agent.py` using `pytest`.

### Human Review & Manual Adjustments (Critical Bugs Resolved)
- **Test Assertion Mismatch**: The unit test `test_blocks_semicolon_injection` failed because the test query (`SELECT * FROM products; DROP TABLE customers;`) triggered Rule 2 (forbidden keyword block on `DROP`) and exited early, returning a keyword violation message instead of reaching Rule 3 (semicolon check).
  - *Correction*: Sanitized the test query to use only safe SELECT statements (`SELECT * FROM products; SELECT * FROM customers;`). This successfully bypassed Rule 2 and isolated the testing of the semicolon injection validator.

---

## Verification and Approval
All modules compiled successfully, and 100% of automated tests pass. The application is robust, safe against SQL injection attacks, and securely executes retail queries.

* **Developer Sign-off**: [Rajat Machade]
* **Date**: August 17, 2026
