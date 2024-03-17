import pandas as pd
import re
from datetime import datetime
from json_handler import load_config

config = load_config()
pd.set_option('display.max_columns', 10)


def extract_store_name(row):
    description = str(row['תאור מורחב']) if pd.notna(row['תאור מורחב']) else ''

    if row['תיאור'] == 'חיוב אשראי':
        return description
    else:
        parts = description.split('ב-')
        # If there are more than two 'ב-', join the parts after the second 'ב-'
        if len(parts) > 2:
            return 'ב-'.join(parts[2:]).strip()
        else:
            return ''  # Return an empty string if the pattern doesn't match as expected


def extract_ironing_date(row):
    if row['תיאור'] == 'חיוב אשראי':
        return row['תאריך'].date()
    if row['תיאור'] == 'כרטיס דביט':
        # Search for a date pattern in 'תאור מורחב'
        match = re.search(r'מתאריך (\d{2}/\d{2}/\d{2})', row['תאור מורחב'])
        if match:
            # Convert the found date to a standard format, if needed
            date_str = match.group(1)
            # Assuming the year is in yy format and you want yyyy, you might need to adjust based on your criteria
            date_obj = datetime.strptime(date_str, '%d/%m/%y').date()
            return date_obj
        else:
            return pd.NaT  # Return Not-a-Time for rows without a match
    else:
        return pd.NaT  # Return Not-a-Time for rows that do not have 'כרטיס דביט' as 'תיאור'


def fix_credit_date(row):
    if row['תיאור'] == 'חיוב אשראי':
        transaction_date = row['תאריך'].date()

        # Calculate the first day of the next month
        if transaction_date.month == 12:  # December case
            first_day_next_month = transaction_date.replace(year=transaction_date.year + 1, month=1, day=1)
        else:
            first_day_next_month = transaction_date.replace(month=transaction_date.month + 1, day=1)

        # Set the payment date to be the 10th of the following month
        payment_date = first_day_next_month.replace(day=10)

        return payment_date
    return row['תאריך'].date()


def data_manipulator():
    df = pd.read_excel(f"{config['export_location']}{config['combined_filename']}")
    df['בית עסק'] = df.apply(extract_store_name, axis=1)
    df['מועד גיהוץ'] = df.apply(extract_ironing_date, axis=1)
    df['תאריך'] = df.apply(fix_credit_date, axis=1)
    df = df.drop_duplicates().reset_index(drop=True)  # remove all duplicate entry if there are for some reason.
    df.sort_values(by='תאריך', inplace=True)
    df.to_excel(f"{config['export_location']}{config['combined_filename']}", index=False)
