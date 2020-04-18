# TODO add keys to arrays for performance

# UTILS IMPORT
from src.util_file_and_log import create_file, check_and_create_folders, finish_logging, pdf_file_name
from src.process_pages import fetch_pages, generate_articles

# IMPORTS FOR LAYOUT PROCESSING
from src.layout_utils import get_text_size_of_line, clean_chars_for_bottom_item, determine_title_size_and_footer_items, remove_footer

# PYTHON UTILS
# TODO Evaluate time for benchmark purposes
#import time

check_and_create_folders()

print("Step 1: Started to parse: ", pdf_file_name)
pages, height = fetch_pages(pdf_file_name, 1)

print("Step 2: Started to process magazine")
title_size, bottom_items, bottom_line = determine_title_size_and_footer_items(pages, height)

print("Step 3: Removing footers from magazine")
pages = remove_footer(bottom_items, pages, bottom_line)

output_text_file = create_file()

print("Step 4: Generating Articles from magazine")
generate_articles(pages, title_size, output_text_file)

finish_logging()