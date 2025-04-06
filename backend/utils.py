# backend/utils.py

import os

def ensure_data_dir_exists(data_dir: str):
    """
    Ensures that the specified data directory exists; creates it if it doesn't.
    """
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    else:
        print(f"Data directory already exists: {data_dir}")