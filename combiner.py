import pandas as pd
import os
import glob
from datetime import datetime
from json_handler import load_config

config = load_config()


def process_statement(file_path, statement_type):
    # Load the data
    df = pd.read_excel(file_path)

    if statement_type == 'credit':
        # Adjustments for credit card statement
        df.rename(columns={'תאריך רכישה': 'תאריך', 'שם בית עסק': 'תאור מורחב', 'סכום חיוב': 'בחובה'}, inplace=True)
        df['תיאור'] = 'חיוב אשראי'
        df['בזכות'] = 0  # Assuming no credit amounts in credit card statement
    elif statement_type == 'bank':
        # Bank statements already match the desired structure
        pass

    # Ensure the date column is in datetime format to enable sorting
    df['תאריך'] = pd.to_datetime(df['תאריך'], format='mixed', dayfirst=True).dt.date


    return df[['תאריך', 'תיאור', 'בחובה', 'בזכות', 'תאור מורחב']]

def combine_statements():
    cleaned_data_dir = config['cleaned_data_location']
    export_data_dir = config['export_location']
    combined_statements = []

    # Process each file in the cleaned data directory
    for file_path in glob.glob(os.path.join(cleaned_data_dir, '*.xlsx')):
        file_name = os.path.basename(file_path)
        if 'Export' in file_name:
            combined_statements.append(process_statement(file_path, 'credit'))
        else:
            combined_statements.append(process_statement(file_path, 'bank'))

    # Combine all processed statements
    combined_df = pd.concat(combined_statements, ignore_index=True)
    combined_df.sort_values(by='תאריך', inplace=True)

    # Save the combined DataFrame
    combined_path = os.path.join(export_data_dir, 'combined_statement.xlsx')
    combined_df.to_excel(combined_path, index=False)

    print(f"Combined statement saved to {combined_path}")


# Example usage


