# Retail SQL Data Analyst Agent
An autonomous, context-aware SQL Agent built using **LangGraph** and the **Tiger AI Gateway (LLM)**. This system translates natural language business questions into precise, read-only MySQL queries, executes them securely, and synthesizes raw database records into natural, professional business insights.

The system features robust safety middleware (SQL safety guardrails) to prevent database manipulation or data destruction, full conversational history (memory) to handle complex contextual follow-up questions, and a human-in-the-loop developer verification interface.

---

## Project Directory Structure
For the system to run correctly, your directory must be structured as follows:
```text
Sql_Agentic/
├── data/
│   ├── stores.csv
│   ├── products.csv
│   ├── customers.csv
│   ├── sales_transactions.csv
│   └── returns.csv
├── database/
│   ├── mysql_schema.sql
│   └── load_data.py
├── evidence/
│   ├── ai_usage_log.md
│   ├── architecture_diagram.md
│   └── human_review_notes.md
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── graph.py
│   ├── memory.py
│   ├── safety.py
│   ├── sql_tools.py
│   └── tiger_gateway_client.py
├── tests/
│   ├── test_agent.py
│   └── test_safety.py
├── .env.example
├── README.md
└── requirements.txt
```

---

## 1. Installation & Environment Setup (Windows PowerShell)

Follow these steps to set up a clean, isolated virtual environment on Windows:

### Step 1.1: Open PowerShell and Navigate to Root
Open Windows PowerShell (as Administrator if required) and navigate to your project directory:
```powershell
cd "C:\Users\rajat.machade\Desktop\Sql_Agentic"
```

### Step 1.2: Set Execution Policy (If Script Execution is Blocked)
If you get a script execution error when trying to activate your virtual environment, run the following command to allow script execution for this terminal session:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Step 1.3: Create and Activate the Virtual Environment
Create a new virtual environment named `venv` and activate it:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
*(Your terminal prompt should now show `(venv)` at the beginning, indicating activation is successful.)*

### Step 1.4: Install Required Dependencies
Install all package dependencies from the `requirements.txt` file:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Database Setup & Data Ingestion (MySQL)

This step guides you through creating the database tables and executing the automated data loader.

### Step 2.1: Run the Database Schema Script
1. Open **MySQL Workbench** and connect to your local MySQL instance.
2. Click **File > Open SQL Script...** and select `database/mysql_schema.sql`.
3. Click the **Lightning Bolt icon (⚡)** to execute the entire script. This will create the database `retail_agent_assignment` and the 5 normalized schemas: `stores`, `products`, `customers`, `sales_transactions`, and `returns`.

### Step 2.2: Load Data using the Python Loader
The CSV datasets contain dates formatted as `DD-MM-YYYY` or `DD/MM/YYYY`, which standard MySQL database engines reject (MySQL expects `YYYY-MM-DD`).
The provided `load_data.py` script automatically cleans, converts, and ingests these records.

Ensure your raw CSV datasets are inside the `data/` directory, and run the ingestion script from your PowerShell terminal:
```powershell
python database/load_data.py
```
**Expected Output:**
```text
--- Starting Automated Data Loading Script ---
Clearing existing table records...
Prior records successfully cleared.

Ingesting datasets...
Successfully loaded 15 rows into table: 'stores'
Successfully loaded 10 rows into table: 'products'
...
--- Initial Verification Row Counts ---
Table 'stores': (15,) rows verified in MySQL database.
Table 'products': (10,) rows verified in MySQL database.
...
Database connection closed. Ingestion process complete.
```

---

## 3. Environment Variables Configuration (Tiger AI Gateway)

### Step 3.1: Configure the `.env` File
Create a new file named `.env` in the root folder of your project (you can duplicate `.env.example` and rename it). Paste your specific Tiger AI Gateway details and MySQL database credentials:

```ini
# Database Configurations
MYSQL_HOST="localhost"
MYSQL_PORT="3306"
MYSQL_DATABASE="retail_agent_assignment"
MYSQL_USER="root"
MYSQL_PASSWORD="your_mysql_password_here"

# Tiger AI Gateway Configuration
TIGER_AI_GATEWAY_URL="https://api.ai-gateway.tigeranalytics.com"
TIGER_AI_GATEWAY_API_KEY="your_tiger_gateway_api_key_here"
TIGER_AI_GATEWAY_MODEL="your_provided_model_name_here"
```

### Step 3.2: Critical Encoding Note (UTF-8 vs UTF-16)
If you create or save `.env` using Windows PowerShell command-line utilities, it may default to **UTF-16 LE** encoding with a Byte Order Mark (BOM). The `python-dotenv` library strictly expects **UTF-8**, and will return `None` (null) for all variables if saved in UTF-16.

**To resolve or verify UTF-8 Encoding:**
1. Open your `.env` file in **Notepad**.
2. Click **File > Save As**.
3. In the **Encoding** dropdown located next to the Save button, select **UTF-8** and hit Save.

### Step 3.3: Submission Security Policy
* **CRITICAL SECURITY RULE**: Do **NOT** include your active `.env` file in your final submission zip folder (`empid_emp_name_agenticAI_L2.zip`).
* The evaluator will use your **`.env.example`** template and run your project with their own local MySQL password and personal Tiger AI Gateway API key. Excluding `.env` is mandatory to pass the "No secrets in code" submission check.

---

## 4. Running the Application

Launch the interactive, conversational command-line console. Always run the module from the root directory to ensure correct package import resolutions:

```powershell
python -m src.app
```

### Prompt Scenarios to Test:

1. **Analytical Query**:
   * *User 👤:* `what are the top 3 selling product categories by total sales volume?`
   * *Agent 🤖:* Translates to SQL, runs on MySQL, and returns a conversational summary of your top 3 categories with exact volume numbers.

2. **Conversational Memory Follow-up** (Context-aware tracking):
   * *User 👤:* `what is the total sales amount?`
   * *Agent 🤖:* Returns the sum of sales amounts.
   * *User 👤:* `show only for the online channel` *(The agent remembers the context and filters by online channel sales!)*

3. **Safety Guardrail Violation**:
   * *User 👤:* `DELETE FROM stores WHERE store_id = 'S001';`
   * *Agent 🤖:* Intercepted! The security middleware stops the query before it hits the database and displays: `Security Violation: Violation: Query contains forbidden modification keyword 'DELETE'.`

---

## 5. Running the Automated Tests

Verify system behavior, API endpoints, and database connection pools using `pytest`:

```powershell
python -m pytest
```

The test runner will automatically locate and execute the 7 unit validation cases across:
* **`tests/test_safety.py`**: Verifies that standard read-only queries are allowed, while malicious keyword edits and stacked semicolon injections are securely blocked.
* **`tests/test_agent.py`**: Validates database connectivity, schemas, and queries.

**Expected Output:**
```text
============================= test session starts =============================
collected 7 items

tests/test_safety.py .....                                               [ 71%]
tests/test_agent.py ..                                                   [100%]

============================== 7 passed in 0.92s ==============================
```
