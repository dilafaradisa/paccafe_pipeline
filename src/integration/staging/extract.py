from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import sqlalchemy
from datetime import datetime, timedelta
from src.utils.helper import etl_log, read_etl_log 

load_dotenv()

SRC_DB_HOST=os.getenv("SRC_POSTGRES_HOST")
SRC_DB_USER=os.getenv("SRC_POSTGRES_USER")
SRC_DB_PASSWORD=os.getenv("SRC_POSTGRES_PASSWORD")
SRC_DB_PORT=os.getenv("SRC_POSTGRES_PORT")
SRC_DB_NAME=os.getenv("SRC_POSTGRES_DB") 


CRED_PATH = os.getenv("CRED_PATH")
KEY_SPREADSHEET = os.getenv("SPREADSHEET_KEY")
MODEL_PATH = os.getenv("MODEL_PATH")

def extract_sheet(sheet_name: str, spreadsheet_key: str, cred_path):
    
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
        
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(spreadsheet_key)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        df = pd.DataFrame(data)
        df.columns = df.iloc[0]
        df = df[1:].copy()
        df.reset_index(drop=True, inplace=True)

        log_message = {
            "step" : "extraction",
            "component" : "source",
            "status" : "success",
            "table_name" : sheet_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return df
    except Exception as e:
        
        log_message = {
            "step" : "extraction",
            "component" : "source",
            "status" : "failed",
            "table_name" : sheet_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
    
    finally:
        etl_log(log_message)

def extract_database(table_name: str):
    try:
        conn = create_engine(f"postgresql://{SRC_DB_USER}:{SRC_DB_PASSWORD}@{SRC_DB_HOST}:{SRC_DB_PORT}/{SRC_DB_NAME}")
        
        # get data from previous process
        filter_log = {
            "step" : "extraction",
            "component" : "source",
            "table_name" : table_name,
            "status" : "success"
        }
        
        # get recent success extraction date
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
        
        query = f"SELECT * FROM {table_name} WHERE created_at > %s::timestamp"
        
        # Execute the query
        df = pd.read_sql(sql=query, con=conn, params=(etl_date,))
        
        # Create a success log message
        log_message = {
            "step" : "extraction",
            "component" : "source",
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
            "component" : "source",
            "status" : "failed",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
        
    finally:
        # Save the log message
        etl_log(log_message)

