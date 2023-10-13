import boto3
import os
from dotenv import load_dotenv
from pdf2image import convert_from_path
import pandas as pd
import pdb
from merge_dataframes import merge_dataframes
import argparse

# Load AWS credentials and region from .env file
load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')

# CELL 2

# Initialize the Textract client
client = boto3.client('textract', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

# Create an argument parser
parser = argparse.ArgumentParser(description="Generate an output path based on the PDF file path")
parser.add_argument("pdf_path", help="Path to the PDF file")
args = parser.parse_args()

# Convert each page of the PDF to images and process with Textract
images = convert_from_path(args.pdf_path)

# Define the subfolder name for CSV files
output_folder = 'data/output'

# Generate the CSV folder path by manipulating the PDF path
pdf_base_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
csv_folder = os.path.join(output_folder, pdf_base_name)

# Create the subfolder if it doesn't exist
if not os.path.exists(csv_folder):
    os.mkdir(csv_folder)

for page_number, image in enumerate(images, start=1):

    # Define the CSV file path with the subfolder
    csv_path = os.path.join(csv_folder, 'page_{}.csv'.format(page_number))

    # Save the PNG image to a temporary file
    image.save('page_{}.png'.format(page_number), 'PNG')

    # Read the local image
    with open('page_{}.png'.format(page_number), 'rb') as image_file:
        image_binary = image_file.read()

    # Call Textract to analyze the image
    response = client.detect_document_text(
        Document={
            'Bytes': image_binary
        }
    )

    # CELL 3

    # Define the expected text in eight consecutive lines
    expected_text = ["1", "2", "3", "4", "5", "6", "7"]

    # Initialize a counter to keep track of consecutive matches
    consecutive_matches = 0

    # Store information about the seven lines
    lines = []

    block_no = 0
    last_sequence_block = -1

    # Iterate through the Textract response blocks
    for block in response['Blocks']:
        block_no += 1
        if block['BlockType'] == 'LINE':
            text = block['Text'].strip()
            if text == expected_text[consecutive_matches]:
                consecutive_matches += 1
                lines.append(block)
                if consecutive_matches == 7:
                    last_sequence_block = block_no
                    print("Seven consecutive lines with the expected text were found.")
                    break
            else:
                consecutive_matches = 0  # Reset the counter if the text doesn't match
                lines = []

    else:
        if consecutive_matches != 7:
            print("Seven consecutive lines with the expected text were not found.")

    # Save the page object
    page_object = response['Blocks'][0]  # Assuming the page object is the first block

    # CELL 4

    vertical_lines = []

    for i, line in enumerate(lines):
        # Extract the bounding box coordinates from the line object
        bbox = line['Geometry']['BoundingBox']
        left = bbox['Left']
        top = bbox['Top']
        width = bbox['Width']
        height = bbox['Height']

        # Calculate the coordinates of the bounding box (just as an fyi in case it's useful somewhere else)
        x1 = left
        x2 = left + width
        y1 = 1 - top
        y2 = 1 - top + height
        # create a center x coordinate of the bounding box
        center_x = x1 + width / 2

        vertical_lines.append(center_x)

    # CELL 5

    # Initialize seven groups to store LINE objects
    line_groups = [[] for _ in range(7)]

    for block in response['Blocks'][last_sequence_block:]:
        if block['BlockType'] == 'LINE':
            bbox = block['Geometry']['BoundingBox']
            left = bbox['Left']
            width = bbox['Width']

            # Calculate the center_x coordinate of the LINE object
            center_x = left + width / 2

            # Find the closest vertical line to the center_x
            closest_line_index = min(range(len(vertical_lines)), key=lambda i: abs(center_x - vertical_lines[i]))

            # Add the LINE object to the corresponding group
            line_groups[closest_line_index].append(block)

    # CELL 6

    import pandas as pd

    # Create a dictionary to store the resulting data
    result_data = {
        'Nummer der Eintragung': [],
        'a) Firma b) Sitz c) Gegenstand des Unternehmens': [],
        'Grundkapital oder Stammkapital DM / EUR': [],
        'Vorstand, persönlich haftende Gesellschafter, Geschäftsführer, Abwickler': [],
        'Prokura': [],
        'Rechtsverhältnisse': [],
        'a) Tag der Eintragung und Unterschrift b) Bemerkungen': []
    }

    # Create a pandas DataFrame to store the resulting data
    df = pd.DataFrame(result_data)

    entry_numbers = []

    # Initialize a flag to indicate whether to skip the first number for gathering divider coordinates
    skip_first_number = True

    # Initialize a list to store the upper y coordinates
    divider_coordinates = []

    # Iterate through line_group[0]
    for i, block in enumerate(line_groups[0]):
        # Check if the 'Text' is a number
        if block['Text'].isdigit():
            entry_numbers.append(block['Text'])
            if skip_first_number:
                # Skip the first number
                skip_first_number = False
                continue

            # Save the upper y coordinate to the list
            divider_coordinates.append(1 - block['Geometry']['BoundingBox']['Top'] + 0.02)

    # add entry numbers to df at the first column

    # initialize single_entry flag to False
    single_entry = False

    if len(entry_numbers) == 1:
        df.loc[0] = [None] * len(df.columns)

        # create a string of the texts from each list in line_groups
        joined_lines = [' '.join([obj['Text'] for obj in group]) for group in line_groups]

        # append joined_lines as first row of df
        df.loc[0] = joined_lines

        # set single_entry flag to True
        single_entry = True


    else:
        df.iloc[:, 0] = entry_numbers
        
    # CELL 7

    numbers_to_check = divider_coordinates

    for index, list_of_blocks in enumerate(line_groups[1:]):

        # break loop if single entry is True
        if single_entry:
            break

        remaining_objects = []

        # Initialize lists to store blocks that meet the condition
        result_lists = [[] for _ in range(len(numbers_to_check))]

        # Check if numbers_to_check is empty
        if not numbers_to_check:
            # Append list_of_blocks to result_lists and skip the loop
            result_lists.append(list_of_blocks)
        else:
            # Iterate through the blocks
            for block in list_of_blocks:
                assigned = False  # Flag to check if the block has been assigned to a list
                for i, number in enumerate(numbers_to_check):
                    if 1 - block['Geometry']['BoundingBox']['Top'] > number:
                        result_lists[i].append(block)
                        assigned = True
                        break  # Break the loop once assigned to a list

                if not assigned:
                    remaining_objects.append(block)

        # Join result_lists to create strings with line breaks preserved
        joined_result_lists = ["\n".join([block['Text'] for block in result_list]) for result_list in result_lists]

        # do the same for remaining_objects
        joined_remaining_objects = "\n".join([block['Text'] for block in remaining_objects])

        # append joined reimaining objects to the end of joined result lists
        joined_result_lists.append(joined_remaining_objects)

        # add joined results list to column number index
        df.iloc[:, index+1] = joined_result_lists

    # CELL 8

    # Modify the CSV save code to save the CSV to the subfolder
    df.to_csv(csv_path, index=False)

    # Clean up temporary PNG files
    os.remove('page_{}.png'.format(page_number))

merge_dataframes(csv_folder)