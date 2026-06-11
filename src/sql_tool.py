import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

# Build the PostgreSQL connection string
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize the database engine
engine = create_engine(DB_URL)

def execute_sql(query: str) -> str:
    """
    Executes a raw SQL query and returns the results.
    If the query fails, it returns the error message for the LLM to read.
    """
    try:
        with engine.connect() as connection:
            # text() safely wraps the raw SQL string
            result = connection.execute(text(query))
            
            # If it's an INSERT/UPDATE/DELETE, there are no rows to fetch
            if not result.returns_rows:
                connection.commit()
                return "Query executed successfully."

            rows = result.fetchall()
            columns = result.keys()
            
            if not rows:
                return "Query executed successfully, but returned no results."
            
            # Format output as a readable string for the LLM
            output = f"Columns: {', '.join(columns)}\n"
            for row in rows:
                output += f"{row}\n"
                
            return output
            
    except SQLAlchemyError as e:
        # THE CRITICAL AGENTIC PATTERN: 
        # Intercept the error and return it as text instead of crashing.
        return f"SQL Execution Error: {str(e)}. Please correct your SQL syntax and try again."
    

if __name__ == "__main__":
    # Test 1: A valid query
    print("--- Good Query ---")
    print(execute_sql("SELECT 1 AS test_column;"))
    
    # Test 2: An intentionally broken query (misspelled SELECT)
    print("\n--- Bad Query ---")
    print(execute_sql("SELEECT * FROM non_existent_table;"))