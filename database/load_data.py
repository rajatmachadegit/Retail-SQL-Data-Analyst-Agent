import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from the root .env file
load_dotenv()

# Retrieve database connection parameters safely
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = os.getenv("MYSQL_PORT", "3306")
DB_NAME = os.getenv("MYSQL_DATABASE", "retail_agent_assignment")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    return mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def load_csv_to_dataframe(file_path):
    """Loads a CSV file into a pandas DataFrame, handling potential path or encoding issues."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing critical dataset at path: {file_path}")
    return pd.read_csv(file_path)

def clean_and_convert_dates(df, date_columns, table_name=""):
    """Converts various date formats (DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD) to MySQL YYYY-MM-DD."""
    for col in date_columns:
        if col in df.columns:
            # Track original non-null values to verify if parsing introduced new nulls
            original_non_null_count = df[col].notna().sum()

            # 1. Try parsing with dayfirst=True (ideal for DD-MM-YYYY and DD/MM/YYYY)
            parsed = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

            # 2. Fallback: If parsing introduced new nulls, try standard automatic parsing
            if parsed.notna().sum() < original_non_null_count:
                parsed_alt = pd.to_datetime(df[col], errors='coerce')
                # Use alternative only if it successfully parsed more dates
                if parsed_alt.notna().sum() > parsed.notna().sum():
                    parsed = parsed_alt

            # 3. Diagnose parsing failures
            new_non_null_count = parsed.notna().sum()
            if new_non_null_count < original_non_null_count:
                failed_mask = df[col].notna() & parsed.isna()
                failed_samples = df.loc[failed_mask, col].unique()[:5]
                print(f"\n[WARNING] Table '{table_name}', column '{col}': "
                      f"Failed to parse {original_non_null_count - new_non_null_count} date values.")
                print(f"Sample of raw values that failed parsing: {failed_samples}")
                print("Ensure these values match standard date formats (like DD-MM-YYYY or YYYY-MM-DD).\n")

            # Format back to MySQL's YYYY-MM-DD (NaT is correctly handled as None)
            df[col] = parsed.dt.strftime('%Y-%m-%d')
    return df

def insert_dataframe_to_table(cursor, table_name, df):
    """Inserts all rows from a pandas DataFrame into the designated MySQL table."""
    # Replace all pandas NaN/NaT values with None so they translate to SQL NULLs
    df = df.where(pd.notnull(df), None)

    # Generate the parameterized INSERT SQL statement
    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Prepare rows as list of tuples for fast batch execution
    data_tuples = [tuple(x) for x in df.to_numpy()]

    cursor.executemany(insert_query, data_tuples)
    print(f"Successfully loaded {len(df)} rows into table: '{table_name}'")

def main():
    print("--- Starting Automated Data Loading Script ---")

    # Define files and their corresponding database tables in loading order
    # (Foreign Key dependencies require parents to load before child tables)
    datasets = [
        {"file": "data/stores.csv", "table": "stores", "dates": []},
        {"file": "data/products.csv", "table": "products", "dates": []},
        {"file": "data/customers.csv", "table": "customers", "dates": ["signup_date"]},
        {"file": "data/sales_transactions.csv", "table": "sales_transactions", "dates": ["order_date"]},
        {"file": "data/returns.csv", "table": "returns", "dates": ["return_date"]}
    ]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Safely clear old data in reverse execution order to respect constraints
        print("\nClearing existing table records to prevent primary key conflicts...")
        tables_to_clear = ["returns", "sales_transactions", "customers", "products", "stores"]
        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        print("Prior records successfully cleared.")

        # Process, transform, and load each CSV dataset
        print("\nIngesting datasets...")
        for ds in datasets:
            file_path = ds["file"]
            table_name = ds["table"]
            date_cols = ds["dates"]

            # Load
            df = load_csv_to_dataframe(file_path)

            # Transform (passing table_name for descriptive logging)
            df = clean_and_convert_dates(df, date_cols, table_name)

            # Load to DB
            insert_dataframe_to_table(cursor, table_name, df)

        conn.commit()
        print("\nDatabase transactions committed successfully!")

        # Capture and verify final database row counts
        print("\n--- Initial Verification Row Counts ---")
        for ds in datasets:
            table_name = ds["table"]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()
            print(f"Table '{table_name}': {count[0]} rows verified in MySQL database.")

    except mysql.connector.Error as db_err:
        print(f"\n[Database Error]: {db_err}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"\n[System Error]: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("\nDatabase connection closed. Ingestion process complete.")

if __name__ == "__main__":
    main()