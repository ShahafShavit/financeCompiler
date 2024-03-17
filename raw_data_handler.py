import pandas as pd
import re
import os
from json_handler import load_config

config = load_config()

def is_date(string):
    return bool(re.match(r"\d{1,2}/\d{1,2}/\d{4}", string))

def process_bank_statement(file_path):
    df = pd.read_excel(file_path)
    pd.set_option('display.max_columns', 10)
    header_index = 1
    table_headers = df.iloc[header_index]
    df.columns = table_headers
    df = df[2:]
    df.drop([table_headers[1],table_headers[3],table_headers[6]], axis=1, inplace=True)
    table_headers = df.columns
    filtered_df = df[~df[table_headers[5]].str.contains('\*', na=False)].copy()
    filtered_df.drop(table_headers[5], axis=1,inplace=True)

    # filtered_df.to_excel(f"{config['cleaned_data_location']}{file_path.split('/')[1]}", index=False)
    return filtered_df


# Define the function to process the credit card statement.
def process_credit_card_statement(file_path):
    # Read the Excel file into a DataFrame.
    df = pd.read_excel(file_path)
    pd.set_option('display.max_columns', 10)

    # Filter the DataFrame for rows containing a date or header identifier.
    df_filtered = df[df.iloc[:, 0].apply(lambda x: is_date(str(x)) or "תאריך רכישה" in str(x))]

    # Identify the indices where headers occur.
    header_indices = df_filtered[df_filtered.iloc[:, 0] == "תאריך רכישה"].index
    #print(header_indices)
    # print(df_filtered)
    # Extract the first table including headers.
    first_table = df_filtered.loc[header_indices[0]:header_indices[1]-1]
    # print(first_table)
    first_table_headers = first_table.iloc[0]  # This is the header row.
    first_table = first_table[1:]  # Drop the header row.

    first_table.columns = first_table_headers # Assign correct column names
    first_table.drop(first_table.columns[5:], axis=1, inplace=True)
    #print(first_table.columns[6:])
    #print(first_table)
    # Extract the second table excluding headers.
    second_table = df_filtered.loc[header_indices[1]:]

    second_table = second_table[1:]  # Drop the header row.

    second_table.drop(second_table.columns[1], axis=1, inplace=True)
    second_table.drop(second_table.columns[5:], axis=1, inplace=True) # Drop the second column.
    second_table.shift(-1)
    second_table.columns = first_table.columns
    # second_table = second_table[1:]

    # Match the columns to the first table.

    # Concatenate the first and second tables.
    final_df = pd.concat([first_table, second_table], ignore_index=True)
    final_df.drop(final_df.columns[[2,3]],axis=1,inplace=True)
    # final_df.to_excel(f"{config['cleaned_data_location']}{file_path.split('/')[1]}", index=False)
    return final_df


# Example usage

def process_files():
    config = load_config()
    data_location = config['data_location']
    cleaned_data_location = config['cleaned_data_location']

    # Ensure the cleaned data location exists

    os.makedirs(cleaned_data_location, exist_ok=True)

    for item in os.listdir(data_location):
        file_path = os.path.join(data_location, item)

        # Check if it's a file
        if os.path.isfile(file_path):
            if 'Export' in item:
                # This is a credit card statement
                processed_df = process_credit_card_statement(file_path)
            else:
                # Assume it's a bank statement otherwise
                processed_df = process_bank_statement(file_path)

            # Save the processed DataFrame to the cleaned data location
            # Filename remains unchanged, just the location changes
            cleaned_file_path = os.path.join(cleaned_data_location, item)
            processed_df.to_excel(cleaned_file_path, index=False)
            print(f"Cleaned data and saved: ({file_path}) --> ({cleaned_file_path})")

# Now, you can inspect the first few rows of the processed dataframe
# processed_credit_data.to_excel('data/processed_statement.xlsx', index=False)

