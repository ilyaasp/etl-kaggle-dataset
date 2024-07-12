import json

def _read_json_file(file_path):
    """Load json file as given by file_path"""
    with open(file_path, "r") as f:
        return json.load(f)