from src.integration.staging.staging_pipeline import staging_pipeline
from src.integration.warehouse.warehouse_pipeline import warehouse_pipeline

if __name__ == "__main__":

    # run pipeline
    
    staging_pipeline()
    warehouse_pipeline()    