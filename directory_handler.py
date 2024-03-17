from os import makedirs
from json_handler import load_config
def ensure_directories_exist():
    config = load_config()
    """Ensure that all directories listed in the config exist; create them if they don't."""
    for key, path in config.items():
        # Assuming all configuration items ending with '_location' are directories
        if key.endswith('_location'):
            makedirs(path, exist_ok=True)
            print(f"Checked/created directory: {path}")
