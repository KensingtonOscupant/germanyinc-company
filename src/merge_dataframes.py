import pandas as pd
import os

def merge_dataframes(csv_folder):
    # Get a list of all files in the CSV folder
    all_files = os.listdir(csv_folder)

    # Filter for CSV files (files with the ".csv" extension)
    csv_files = [file for file in all_files if file.endswith('.csv')]

    # Initialize an empty dataframe to store the merged data
    merged_df = pd.DataFrame()

    # Iterate through the CSV files and merge them into a single dataframe
    for csv_file in csv_files:
        # Load each CSV file into a dataframe
        df = pd.read_csv(os.path.join(csv_folder, csv_file))

        # Merge the loaded dataframe with the existing merged dataframe
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # Sort the merged dataframe by the 'Nummer der Eintragung' column
    merged_df.sort_values(by=merged_df.columns[0], inplace=True)

    # Identify and handle merged entries
    merged_entries = []

    for index, row in merged_df.iterrows():
        entry_number = row.iloc[0]
        if entry_number in merged_entries:
            # Merge this row with the previous row
            prev_row_index = merged_df.index[merged_df.iloc[0] == entry_number].max() - 1
            prev_row = merged_df.loc[prev_row_index]
            for column in merged_df.columns:
                if pd.isna(prev_row[column]) and not pd.isna(row[column]):
                    prev_row[column] = row[column]
            merged_df.loc[prev_row_index] = prev_row
            merged_df.drop(index, inplace=True)
        elif not pd.isna(entry_number):
            merged_entries.append(entry_number)

    # Now, 'merged_df' contains the combined dataframe with merged entries

    # asve the merged dataframe to a CSV file
    merged_df.to_csv(f"{csv_folder}/merged_dataframe.csv", index=False)