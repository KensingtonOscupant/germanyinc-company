import pdfplumber
import pandas as pd

def is_integer(value):
    """Check if a given value is an integer."""
    try:
        # Check if value is None before trying to convert
        if value is None:
            return False
        int(value)
        return True
    except ValueError:
        return False

def process_rows(all_rows):
    # Placeholder for the result
    result_rows = []

    # Placeholder for the current merged row
    current_row = None

    for row in all_rows:
        # If the row itself is None or empty, skip this iteration
        if row is None or all(pd.isnull(val) for val in row):
            continue

        # If the row has a value in the first column and the value is an integer
        if is_integer(row[0]):
            # If there's a current_row, append it to the result
            if current_row:
                result_rows.append(current_row)
            # Set the current row
            current_row = list(row)
        # If the row does not have a value in the first column or the value is not an integer
        else:
            # Merge the row with the current_row
            if current_row is not None:
                for i in range(1, len(row)):
                    current_row[i] = f"{current_row[i]} {row[i]}"

    # Append the last row if there is one
    if current_row:
        result_rows.append(current_row)

    # Convert the result to a dataframe
    result_df = pd.DataFrame(result_rows, columns=all_rows[0])  # Using the first row as columns

    return result_df

# Open the PDF file
with pdfplumber.open('data/input/3U Holding AG - aktuell - HE-Marburg_HRB_4680+CD-20221004182421.pdf') as pdf:
    # Initialize a list to store all rows (flatten tables)
    all_rows = []

    # Extract tables from each page and append rows to all_rows
    for page in pdf.pages:
        table = page.extract_table()
        if table:
            all_rows.extend(table[2:])  # skip the header rows

# Process the rows
result_df = process_rows(all_rows)

# To display the result or save it
print(result_df)
# Optionally save to a CSV file
result_df.to_csv('data/input/pdfplumber_new_output.csv', index=False)
