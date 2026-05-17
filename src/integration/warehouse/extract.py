import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from src.utils.helper import etl_log, read_etl_log
from datetime import datetime

load_dotenv()

STG_DB_HOST=os.getenv("STG_POSTGRES_HOST")
STG_DB_USER=os.getenv("STG_POSTGRES_USER")
STG_DB_PASSWORD=os.getenv("STG_POSTGRES_PASSWORD")
STG_DB_PORT=os.getenv("STG_POSTGRES_PORT")
STG_DB_NAME=os.getenv("STG_POSTGRES_DB")


def extract_from_staging(table_name: str) -> str:
    try:
        
        # Create connection to the source database
        conn = create_engine(f"postgresql://{STG_DB_USER}:{STG_DB_PASSWORD}@{STG_DB_HOST}:{STG_DB_PORT}/{STG_DB_NAME}")
        
        # Get data from previous process
        filter_log = {
            "step" : "warehouse",
            "component" : "load",
            "status" : "success",
            "table_name" : table_name
        }
        
        # Get the last successful extraction date
        etl_date = read_etl_log(filter_params=filter_log)
        
        # If no previous extraction has been recorder (etl_date is empty), set etl_date to '1111-01-01' indicating initial load
        # Otherwise, retrieve data added since the last successful extraction (etl_date)
        
        if (etl_date["max"][0] == None):
            etl_date = "1111-01-01"
            
        else:
            etl_date = etl_date['max'][0]
        
        # Construct a query to select all columns from the specified table name where 'created_at' is greater than the etl_date
        
        """
        SELECT *
        FROM customers
        WHERE created_at > :etl_date
        """

        # Read the sql file    
        # query = sqlalchemy.text(read_sql(table_name))
        query = f"SELECT * FROM {table_name} WHERE created_at > %s::timestamp"
        
        # Execute the query
        df = pd.read_sql(sql=query, con=conn, params=(etl_date,))
        
        # Create a success log message
        log_message = {
            "step" : "extraction",
            "component" : "staging",
            "status" : "success",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Return the extracted data if successful
        return df
        
    except Exception as e:
        # Create a failed log message
        log_message = {
            "step" : "extraction",
            "component" : "staging",
            "status" : "failed",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
        
    finally:
        # Save the log message
        etl_log(log_message)

def extract_all(table_name: str):
    conn = create_engine(f"postgresql://{STG_DB_USER}:{STG_DB_PASSWORD}@{STG_DB_HOST}:{STG_DB_PORT}/{STG_DB_NAME}")
    
    # select all from the table
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    
    return df
