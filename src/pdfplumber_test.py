import pdfplumber
import csv

# Open the PDF file
with pdfplumber.open('data/2invest AG - aktuell - BW-Mannheim_HRB_335706+Chronologischer_Abdruck-20211221145504.pdf') as pdf:
    # Initialize a list to store the tables
    all_tables = []

    # Extract tables from each page
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            all_tables.append(table)

# Now you have a list of tables, where each table is a list of rows and columns
for table in all_tables:
    for row in table:
        print(row)

# Specify the output CSV file path
output_csv_path = 'pdfplumber_csv_output.csv'

# Write the extracted tabular data to a CSV file
with open(output_csv_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Iterate through each table
    for table in all_tables:
        # Iterate through each row in the table and write it to the CSV
        for row in table:
            csv_writer.writerow(row)