from json import load as js_load

def load_config():
    with open('config.json', 'r') as file:
        config = js_load(file)
    return config