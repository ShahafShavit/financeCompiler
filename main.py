from data_manipulator import data_manipulator
from input_handler import convert_all_xls_files
from raw_data_handler import process_files
from directory_handler import ensure_directories_exist
from combiner import combine_statements
from categorizer import categorizer

ensure_directories_exist()
convert_all_xls_files()
process_files()
combine_statements()
data_manipulator()
categorizer()
