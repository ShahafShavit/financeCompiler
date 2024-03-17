import pandas as pd
import os
import glob
from json_handler import load_config

# Load configuration
config = load_config()

def html_to_excel(html_file_path, output_file_path):
    # Attempt to read the HTML file and save the specified table as an Excel file
    try:
        dfs = pd.read_html(html_file_path)
        df = dfs[2]  # Adjust the index based on which table contains the relevant data
        df.to_excel(output_file_path, index=False)
    except Exception as e:
        print(f"Error converting HTML to Excel for {html_file_path}: {e}")

def convert_file_to_xlsx(file_path):
    base_name = os.path.basename(file_path)
    new_file_name = base_name.replace('.xls', '.xlsx')
    xlsx_file_path = os.path.join(config['data_location'], new_file_name)

    try:
        df = pd.read_excel(file_path)
    except ValueError as e:
        html_to_excel(file_path, xlsx_file_path)
        print(f"File was faulty but successfully converted (HTML) | ({file_path}) --> ({xlsx_file_path})")
    else:
        with pd.ExcelWriter(xlsx_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        print(f"File successfully converted | ({file_path}) --> ({xlsx_file_path})")

def convert_all_xls_files():
    input_dir = config['input_location']
    cleaned_data_dir = config['data_location']
    os.makedirs(cleaned_data_dir, exist_ok=True)

    xls_files = glob.glob(os.path.join(input_dir, '*.xls'))

    for file_path in xls_files:
        convert_file_to_xlsx(file_path)

