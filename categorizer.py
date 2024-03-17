import pandas as pd
import json
from prettytable import PrettyTable
from json_handler import load_config
import ast


def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


# Load mappings
category_to_stores = load_json_data('static/category_to_stores.json')
store_to_category = load_json_data('static/store_to_categories.json')
non_standard_transactions = load_json_data('static/non_standard_transactions.json')
config = load_config()


# Function to update the store_to_categories.json file
def update_store_categories(source="file"):
    store_to_category = load_json_data('static/store_to_categories.json')
    if source == "file":
        # Automatically update store categories from the Excel file
        df = pd.read_excel(f"{config['export_location']}{config['combined_filename']}")

        for index, row in df.iterrows():
            store_name = row['בית עסק']
            category = row['קטגוריה']
            if category[0] != "[":
                if pd.notna(store_name) and pd.notna(category):
                    if store_name in store_to_category:
                        if category not in store_to_category[store_name]:
                            store_to_category[store_name].append(category)
                    else:
                        store_to_category[store_name] = [category]
    # DEPRECATED
    if source == "manual":
        im_done = False
        for store, categories in store_to_category.items():
            if categories == []:
                print(f"Current categories for {store}: {categories}")
                while True:
                    new_category = input("Enter a new category to add (or 0 to move to the next store or 00 to exit): ")
                    if new_category == "0":
                        break  # Exit the loop for the current store
                    elif new_category == "00":
                        im_done = True
                        break
                    elif new_category and new_category not in categories:
                        categories.append(new_category)
                        print(f"Added category '{new_category}'. Current categories: {categories}")
                    else:
                        print("Invalid input or duplicate category.")
                if im_done:
                    break
    # DEPRECATED
    # Write the updated data back to the file
    with open('static/store_to_categories.json', 'w', encoding='utf-8') as file:
        json.dump(store_to_category, file, indent=4, ensure_ascii=False)
    print("Updated categories saved.")


### DEPRECATED BELOW ###
# Grab new stores from the datasheet and add them to the .json file
def update_stores_in_json():
    # Load configuration
    config = load_config()

    # Fixed file paths
    excel_file_path = f"{config['export_location']}{config['combined_filename']}"
    json_file_path = 'static/store_to_categories.json'
    # Load the Excel file
    df = pd.read_excel(excel_file_path)

    # Extract distinct store names
    distinct_stores = df['בית עסק'].dropna().unique()

    # Load or create the JSON structure
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            store_to_categories = json.load(file)
    except FileNotFoundError:
        store_to_categories = {}

    # Update the JSON structure with new stores (if they don't exist)
    updated = False
    for store in distinct_stores:
        if store not in store_to_categories:
            store_to_categories[store] = []  # Initialize with an empty category list
            updated = True

    # Save the updated JSON structure back to the file (if there were any updates)
    if updated:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(store_to_categories, file, indent=4, ensure_ascii=False)
        print("JSON file updated with new stores.")
    else:
        print("No new stores to add.")


def add_non_standard_transaction(description, category):
    file_path = 'static/non_standard_transactions.json'
    non_standard_transactions = load_json_data(file_path)

    # Duplication verification
    if description in non_standard_transactions and category in non_standard_transactions[description]:
        print(f"The category '{category}' already exists for the description '{description}'.")
    else:
        non_standard_transactions.setdefault(description, []).append(category)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(non_standard_transactions, file, indent=4, ensure_ascii=False)
        print(f"Added '{description}' to non-standard transactions with category '{category}'.")


# Function to categorize **A** record by store/non-standard (data is given from the .json files)
# Not called by itself usually
def categorize_transaction(row):
    # Check if the transaction is a standard store name
    store_name = str(row['בית עסק']).strip()
    if store_name != "nan":
        for store, categories in store_to_category.items():
            if store_name in store:
                # Direct comparison after cleaning inputs
                if len(categories) == 1:
                    return categories[0]  # Return the single category
                else:
                    return categories  # Join multiple categories with a comma

    # For non-standard transactions based on the description column
    description = str(row['תיאור']).strip()
    if description in non_standard_transactions:
        categories = non_standard_transactions[description]
        if len(categories) == 1:
            return categories[0]
        else:
            return categories

    return "Uncategorized"

# Categorize the datasheet automatically using categorize_transaction
def categorize_datasheet():
    df = pd.read_excel(f"{config['export_location']}{config['combined_filename']}")
    df['קטגוריה']=df.apply(categorize_transaction,axis=1)
    print("Categorized datasheet by store names.")
    df.to_excel(f"{config['export_location']}{config['combined_filename']}", index=False)


# Identify category per record in case of list in category or uncategorized
def identify_categories():
    df = pd.read_excel(f"{config['export_location']}{config['combined_filename']}")
    untouched = True
    for index, row in df.iterrows():
        if row['קטגוריה'][0] == "[" or row['קטגוריה'] == "Uncategorized":
            table = PrettyTable()
            table.field_names = df.columns.tolist()  # Add column names as field names
            table.add_row(row.tolist())  # Add the current row to the table
            print(table)
            category = input("Please enter any relevant category for given transaction (enter 0 to abort): ")
            if category == "0":
                break
            df.at[index, 'קטגוריה'] = category

            untouched = False
            if row['תיאור'] not in ['חיוב אשראי', 'כרטיס דביט']:
                add_non_standard_transaction(row['תיאור'], category)
    df.to_excel(f"{config['export_location']}{config['combined_filename']}", index=False)
    if untouched:
        print("All transactions are identified properly.")


""" 
סדר פעולות
קובץ מגיע עם עמודת בתי עסק
categorize_datasheet
identify_categories
update_store_categories
"""


def categorizer():
    categorize_datasheet()
    identify_categories()
    update_store_categories()

### WORK ON NON STANDARD CATEGORIES ###
