# config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define variables by reading specific folder paths from the .env file
LOG_FOLDER = os.getenv('LOG_FOLDER', 'processes')
PROCESSED_DATA_FOLDER = os.getenv('PROCESSED_DATA_FOLDER', 'final-data')
RAW_DATA_FOLDER = os.getenv('RAW_DATA_FOLDER', 'app')
IMPORT_FOLDER = os.getenv('IMPORT_FOLDER', 'app/import')
RULES_PATH = os.getenv('RULES_PATH', 'sidebar/demographic')

# Store them in a dictionary (optional, if you need dynamic access)
FOLDER_PATHS = {
    'LOG_FOLDER': LOG_FOLDER,
    'PROCESSED_DATA_FOLDER': PROCESSED_DATA_FOLDER,
    'RAW_DATA_FOLDER': RAW_DATA_FOLDER,
    'APP_FOLDER': IMPORT_FOLDER,
    'RULES_PATH': RULES_PATH
}

# Example: Print the folder paths for debugging
if __name__ == "__main__":
    print("Log Directory:", LOG_FOLDER)
    print("Data Directory:", PROCESSED_DATA_FOLDER)
    print("Backup Directory:", RAW_DATA_FOLDER)
    print("Import Directory:", IMPORT_FOLDER)
    print("Rules Directory:", RULES_PATH)
