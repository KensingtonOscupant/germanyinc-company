import boto3
import os
from dotenv import load_dotenv
from pdf2image import convert_from_path
import pandas as pd
import pdb
from merge_dataframes import merge_dataframes
import argparse
from ocr_pipeline import get_column_borders, get_row_borders, find_header_row, find_record_continued_from_previous_page, clean_image, get_dark_pixels, get_dividers

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

    '''This section of code is used to find the header row with the numbers 1, 2, 3, 4, 5, 6, and 7 by
    checking if there are 7 blocks in a row that meet those criteria.'''

    numbers, last_sequence_block = find_header_row(response)

    # CELL 3.1

    # preprocess image
    image = clean_image(image, response)

    # CELL 4

    '''From the seven numbers in the header row, we can calculate the center x coordinate of 
    each number's bounding box and this way create seven axes, one at the center of each column of the HRA.'''

    x_dividers = []

    # get number of dark pixels in each column and row
    row_list, column_list = get_dark_pixels(image)

    # get the central x coordinate of each number in the header row
    x_coordinates = []
    for number in numbers:
        x_coordinates.append((number['Geometry']['BoundingBox']['Left'] + number['Geometry']['BoundingBox']['Width']/2) * image.size[0])

    # get the column dividers
    x_dividers, x_dividers_absolute = get_dividers(x_coordinates, column_list) # the absolute dividers are just used if we want to plot the dividers

    # CELL 5

    '''We group all the LINE objects into seven groups based on their proximity to the seven axes.'''

    # Initialize seven groups to store LINE objects
    line_groups = [[] for _ in range(7)]

    for block in response['Blocks'][last_sequence_block:]:
        if block['BlockType'] == 'LINE':
            bbox = block['Geometry']['BoundingBox']
            left = bbox['Left']
            width = bbox['Width']

            # Calculate the center_x coordinate of the LINE object
            center_x = left + width / 2

            # Iterate through x_dividers to check where center_x belongs
            for i, divider in enumerate(x_dividers):
                if center_x < divider:
                    # Append the LINE object to the corresponding list
                    line_groups[i].append(block)
                    break
            else:
                # If the center_x is greater than the last divider, assign it to the last group
                line_groups[-1].append(block)

    # get the y coordinates of the divider lines

    # get the bottom coordinate of the first numbers object
    y_coordinates = []

    # append bottom coordinate of one of the numbers in the header row
    y_coordinates.append((numbers[0]['Geometry']['BoundingBox']['Top'] + numbers[0]['Geometry']['BoundingBox']['Height']) * image.size[1])

    print(len(line_groups[0]))
    # append the bottom coordinate of all objects in line_groups[0]
    for line in line_groups[0]:
        y_coordinates.append((line['Geometry']['BoundingBox']['Top'] + line['Geometry']['BoundingBox']['Height']) * image.size[1])

    # append the bottom border of the page
    y_coordinates.append(image.size[1]-15)

    y_dividers, y_dividers_absolute = get_dividers(y_coordinates, row_list) # the absolute dividers are just used if we want to plot the dividers

    filtered_line_groups = []

    # check if there is a continued entry from the previous page
    if find_record_continued_from_previous_page(line_groups, y_dividers):
        continued_entry = find_record_continued_from_previous_page(line_groups, y_dividers)
        # add the record to the filtered_line_groups
        filtered_line_groups.append(continued_entry)
        print("continued entry found")

    # Iterate through pairs of adjacent y_dividers
    for i in range(len(y_dividers) - 1):
        lower_bound = y_dividers[i]
        print("lower_bound", lower_bound)
        upper_bound = y_dividers[i + 1]
        print("upper_bound", upper_bound)

        # Initialize a filtered group for this range
        filtered_group = []

        # Iterate through the line groups
        for group in line_groups:
            # Filter and join the LINE texts in the current group for this range
            filtered_text = "\n".join(line['Text'] for line in group if lower_bound <= (line['Geometry']['BoundingBox']['Top'] + line['Geometry']['BoundingBox']['Height'] * 0.5) < upper_bound) # get the middle of the line object
            
            filtered_group.append(filtered_text)

        # Add the filtered group to the result
        filtered_line_groups.append(filtered_group)

    df = pd.DataFrame(filtered_line_groups)

    # if the first column of the last row has any non-numerical characters, drop the last row
    if not df.iloc[-1, 0].isdigit():
        df = df.drop(df.tail(1).index)
        print("dropped the last row because it was not a number. Note: Log this in the future.")

    # Modify the CSV save code to save the CSV to the subfolder
    df.to_csv(csv_path, index=False)

    # Clean up temporary PNG files
    os.remove('page_{}.png'.format(page_number))

merge_dataframes(csv_folder)