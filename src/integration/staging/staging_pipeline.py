import os
from src.integration.staging.extract import extract_sheet, extract_database
from src.integration.staging.load import load_to_staging

CRED_PATH = os.getenv("CRED_PATH")
KEY_SPREADSHEET = os.getenv("SPREADSHEET_KEY")
MODEL_PATH = os.getenv("MODEL_PATH")

def staging_pipeline():
    # extract data from google sheet
    print("extracting data from google sheet...")
    df_store = extract_sheet(sheet_name="store_branch", spreadsheet_key=KEY_SPREADSHEET, cred_path=CRED_PATH)
    
    print("loading data to staging for table: store_branch...")
    load_to_staging(data=df_store, schema="public", table_name="store_branch", idx_name="store_id")

    table_names = {
        "customers":"customer_id",
        "employees":"employee_id",
        "inventory_tracking":"tracking_id",
        "products":"product_id",
        "orders":"order_id",
        "order_details":"order_detail_id"
    }
    # extract from database
    print("extracting data from database...")
    for table, idx in table_names.items():
        print(f"Processing table: {table}...")
        data = extract_database(table_name=table)

        print(f"Loading data to staging for table: {table}...")
        try:
            load_to_staging(data=data, schema="public", table_name=table, idx_name=idx)
            print(f"Successfully loaded data for table: {table}")
        except Exception as e:
            print(f"Error occurred while loading table {table}: {e}")
        


