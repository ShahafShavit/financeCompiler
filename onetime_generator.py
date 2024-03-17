import pandas as pd
import json

def store_to_categoies():
    df = pd.read_csv("הוצאות שנתיות 2024 - גיליון16.csv")  # Adjust based on the actual data format

    # Initialize an empty dictionary to hold the store-category mappings
    store_categories = {}

    # Iterate through the DataFrame to fill the dictionary
    for index, row in df.iterrows():
        for category in df.columns:
            store_name = row[category]
            if pd.notna(store_name):  # Check if the store name exists in this category
                if store_name not in store_categories:
                    store_categories[store_name] = []
                store_categories[store_name].append(category)

    # Convert the dictionary to JSON
    json_output = json.dumps(store_categories, ensure_ascii=False)
    with open('static/store_to_categories.json', 'w', encoding='utf-8') as f:
        f.write(json_output)

def category_to_stores():
    df = pd.read_csv("הוצאות שנתיות 2024 - גיליון16.csv")  # Or adjust based on your actual data input

    # Initialize an empty dictionary for category-store mappings
    category_stores = {}

    # Iterate through each category to fill the dictionary
    for category in df.columns:
        stores = df[category].dropna().unique().tolist()  # Removing NaN values and duplicate stores
        category_stores[category] = stores

    # Convert the dictionary to JSON
    json_output = json.dumps(category_stores, ensure_ascii=False, indent=4)
    with open('static/category_to_stores.json', 'w', encoding='utf-8') as f:
        f.write(json_output)

store_to_categoies()
category_to_stores()