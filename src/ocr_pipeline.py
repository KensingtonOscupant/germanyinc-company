from PIL import ImageDraw
import numpy as np

def get_column_borders(line_object, image, threshold=100, tile_width=2, padding=3):
    """This function takes a line object and returns the coordinates of the left and right borders of the column"""
    # get bounding box coordinates of line 1
    bbox = line_object['Geometry']['BoundingBox']
    bbox_left = bbox['Left']
    bbox_top = bbox['Top']
    bbox_width = bbox['Width']
    bbox_height = bbox['Height']

    # Convert initial coordinates to pixel coordinates
    width, height = image.size
    initial_left = int(bbox_left * width)
    initial_top = int(bbox_top * height)
    initial_right = int((bbox_left + bbox_width) * width)
    initial_bottom = int((bbox_top + bbox_height) * height)

    tile_height = initial_bottom - initial_top  # Height remains the same for all tiles

    # Initialize the left and right coordinates for checking the right side, with a bit of padding
    left_coordinate_checking_right = initial_right + padding
    right_coordinate_checking_right = initial_right + padding + tile_width

    # Initialize the left and right coordinates for checking the left side
    left_coordinate_checking_left = initial_left - padding - tile_width
    right_coordinate_checking_left = initial_left - padding

    # checking the right side

    while right_coordinate_checking_left < width:
        # print("Evaluating tile at:", left_coordinate_checking_right, right_coordinate_checking_right)

        # Crop the tile
        tile = image.crop((left_coordinate_checking_right, initial_top, right_coordinate_checking_right, initial_bottom))

        # Convert the tile to grayscale
        gray_tile = tile.convert("L")

        # Convert the tile to a list of pixel values
        pixels = list(gray_tile.getdata())

        # Count the number of dark pixels
        dark_pixel_count = sum(1 for pixel in pixels if pixel < threshold)

        # Calculate the total number of pixels in the tile
        total_pixels = tile_width * tile_height

        # Check if at least half of the pixels are dark
        if dark_pixel_count >= 0.5 * total_pixels:
            break  # Half of the pixels are dark, exit the loop
        else:
            left_coordinate_checking_right += 1  # Move the tile one pixel to the right
            right_coordinate_checking_right += 1

    # checking the left side

    while right_coordinate_checking_left < width:
        # print("Evaluating tile at:", left_coordinate_checking_left, right_coordinate_checking_left)

        # Crop the tile
        tile = image.crop((left_coordinate_checking_left, initial_top, right_coordinate_checking_left, initial_bottom))

        # Convert the tile to grayscale
        gray_tile = tile.convert("L")

        # Convert the tile to a list of pixel values
        pixels = list(gray_tile.getdata())

        # Count the number of dark pixels
        dark_pixel_count = sum(1 for pixel in pixels if pixel < threshold)

        # Calculate the total number of pixels in the tile
        total_pixels = tile_width * tile_height

        # Check if at least half of the pixels are dark
        if dark_pixel_count >= 0.5 * total_pixels:
            break  # Half of the pixels are dark, exit the loop
        else:
            left_coordinate_checking_left -= 1  # Move the tile one pixel to the right
            right_coordinate_checking_left -= 1

    # # The 'right' variable now contains the rightmost position where half of the pixels are dark
    # print("Right position where half of the pixels are dark, checking towards the right:", right_coordinate_checking_right)

    # # The 'left' variable now contains the leftmost position where half of the pixels are dark
    # print("Left position where half of the pixels are dark, checking towards the left:", left_coordinate_checking_left)

    # transform coordinates back to relative coordinates
    left_coordinate_checking_left = left_coordinate_checking_left / width
    right_coordinate_checking_right = right_coordinate_checking_right / width

    return left_coordinate_checking_left, right_coordinate_checking_right

def get_row_borders(line_object, image, threshold=100, tile_height=2, padding=3):
    """This function takes a line object and returns the coordinates of the upper and lower borders of the row"""
    # get bounding box coordinates of line 1
    bbox = line_object['Geometry']['BoundingBox']
    bbox_left = bbox['Left']
    bbox_top = bbox['Top']
    bbox_width = bbox['Width']
    bbox_height = bbox['Height']

    # Convert initial coordinates to pixel coordinates
    width, height = image.size
    initial_left = int(bbox_left * width) -4 # making the tile a bit wider to the left
    initial_top = int(bbox_top * height)
    initial_right = int((bbox_left + bbox_width) * width) +4 # making the tile a bit wider to the right
    initial_bottom = int((bbox_top + bbox_height) * height)

    tile_width = initial_right - initial_left  # Width remains the same for all tiles

    top_coordinate_checking_bottom = initial_bottom + padding
    bottom_coordinate_checking_bottom = initial_bottom + padding + tile_height

    top_coordinate_checking_top = initial_top - padding - tile_height
    bottom_coordinate_checking_top = initial_top - padding

    # checking the bottom side

    while bottom_coordinate_checking_bottom < height:
        # print("Evaluating tile at:", top_coordinate_checking_bottom, bottom_coordinate_checking_bottom)

        # Crop the tile
        tile = image.crop((initial_left, top_coordinate_checking_bottom, initial_right, bottom_coordinate_checking_bottom))

        # Convert the tile to grayscale
        gray_tile = tile.convert("L")

        # Convert the tile to a list of pixel values
        pixels = list(gray_tile.getdata())

        # Count the number of dark pixels
        dark_pixel_count = sum(1 for pixel in pixels if pixel < threshold)

        # Calculate the total number of pixels in the tile
        total_pixels = tile_width * tile_height

        # Check if at least half of the pixels are dark
        if dark_pixel_count >= 0.5 * total_pixels:

            # image.crop((initial_left, top_coordinate_checking_bottom-100, initial_right+100, bottom_coordinate_checking_bottom+100)).show()
            break
        else:
            top_coordinate_checking_bottom += 1
            bottom_coordinate_checking_bottom += 1

    # checking the top side

    while top_coordinate_checking_top > 0:
        # print("Evaluating tile at:", top_coordinate_checking_top, bottom_coordinate_checking_top)

        # Crop the tile
        tile = image.crop((initial_left, top_coordinate_checking_top, initial_right, bottom_coordinate_checking_top))

        # Convert the tile to grayscale
        gray_tile = tile.convert("L")

        # Convert the tile to a list of pixel values
        pixels = list(gray_tile.getdata())

        # Count the number of dark pixels
        dark_pixel_count = sum(1 for pixel in pixels if pixel < threshold)

        # Calculate the total number of pixels in the tile
        total_pixels = tile_width * tile_height

        # Check if at least half of the pixels are dark
        if dark_pixel_count >= 0.5 * total_pixels:

            # image.crop((initial_left, top_coordinate_checking_top, initial_right, bottom_coordinate_checking_top)).show()
            break
        else:
            top_coordinate_checking_top -= 1
            bottom_coordinate_checking_top -= 1

    # transform coordinates back to relative coordinates
    top_coordinate_checking_top = top_coordinate_checking_top / height
    bottom_coordinate_checking_bottom = bottom_coordinate_checking_bottom / height

    return top_coordinate_checking_top, bottom_coordinate_checking_bottom

def check_y_coordinate_spacing(numbers):
    """This function takes a list of number objects and checks if the y-coordinate spacing between the numbers"""

    # Get a list of y-coordinates
    y_coordinates = [x['Geometry']['BoundingBox']['Top'] for x in numbers]

    print("The y-coordinates are:", y_coordinates)

    # Calculate the mean distance for each coordinate to the others
    mean_distances = []

    for i, y1 in enumerate(y_coordinates):
        other_y_coordinates = y_coordinates[:i] + y_coordinates[i + 1:]
        mean_distance = sum(abs(y1 - y2) for y2 in other_y_coordinates) / len(other_y_coordinates)
        mean_distances.append(mean_distance)

    print("The mean distances between the y-coordinates are:", mean_distances)

    # Find the largest and second largest mean distances
    mean_distances.sort(reverse=True)
    largest_mean_distance = mean_distances[0]
    second_largest_mean_distance = mean_distances[1] if len(mean_distances) > 1 else 0

    # Check if the largest mean distance is more than three times the second largest mean distance
    if largest_mean_distance > 3 * second_largest_mean_distance and largest_mean_distance > 0.015:
        # Print which number has the largest mean distance
        index_of_largest = mean_distances.index(largest_mean_distance)
        print("One number is way further away than the others. It is number ", numbers[index_of_largest]['Text'])
        return True  # The number with the y-coordinate furthest away is significantly further
    else:
        return False  # The y-coordinate spacing does not meet the criteria

def find_header_row(response):

    '''This section of code is used to find the header row with the numbers 1, 2, 3, 4, 5, 6, and 7 by
    checking if there are 7 blocks that meet those criteria.'''

    # Define the expected text in eight consecutive lines
    expected_text = ["1", "2", "3", "4", "5", "6", "7"]

    # Define the list of words to check for in the previous blocks
    words_to_check = ["Prokura", "Eintragung", "Geschäftsführer"]

    # Initialize a counter to keep track of consecutive matches
    consecutive_matches = 0

    found_words_condition = False  # Flag to indicate if any word from words_to_check is found

    # Store information about the seven lines
    numbers = []

    block_no = 0
    last_sequence_block = -1

    # Iterate through the Textract response blocks
    for block in response['Blocks']:
        block_no += 1
        if block['BlockType'] == 'LINE':
            text = block['Text'].strip()

            # Check if any word from the list of words has appeared in the text
            for word in words_to_check:
                if found_words_condition:
                    break

                if word in text:
                    found_words_condition = True  # Set the flag to True
                    break  # Exit the loop once a word is found

            if found_words_condition and text in expected_text:
                consecutive_matches += 1
                expected_text.remove(text)
                numbers.append(block)
                # print("text: " + text)
                # print("expected_text: " + str(expected_text))
                if consecutive_matches == 7:
                    last_sequence_block = block_no
                    print("All seven expected numbers were found.")
                    break
            else:
                consecutive_matches = 0  # Reset the counter if the text doesn't match
                expected_text = ["1", "2", "3", "4", "5", "6", "7"]
                numbers = []

    else:
        if consecutive_matches != 7:
            print("Not all expected numbers were found.")

    # sort number objects from left to right
    numbers = sorted(numbers, key=lambda x: x['Geometry']['BoundingBox']['Left'])

    check_y_coordinate_spacing(numbers)

    return numbers, last_sequence_block

def find_record_continued_from_previous_page(line_groups, y_dividers):
    smallest_y_divider = min(y_dividers)

    # Initialize an empty list to store the filtered line groups
    filtered_line_groups_no_entry_number = []

    # Iterate through the line_groups
    for group in line_groups:
        # Filter the LINE objects in the current group
        filtered_group = [line for line in group if line['Geometry']['BoundingBox']['Top'] < smallest_y_divider]
        
        # Add the filtered group to the result
        filtered_line_groups_no_entry_number.append(filtered_group)

    # Initialize an empty list to store the joined texts
    joined_texts = []

    # Iterate through the filtered_line_groups

    for group in filtered_line_groups_no_entry_number:
        # join all the texts together and keep the line breaks
        joined_text = '\n'.join([line['Text'] for line in group])

        # Add the joined text to the result
        joined_texts.append(joined_text)

    # if joined_texts[0] is empty, add the number of the previous entry number

    # the previous entry is the last entry of the first column of the previous CSV in the folder: First idea:
    # previous_csv_path = os.path.join(csv_folder, 'page_{}.csv'.format(page_number - 1))
    # previous_df = pd.read_csv(previous_csv_path)
    # previous_entry_number = previous_df.iloc[-1, 0]

    previous_entry_number = "33"

    if joined_texts[0] == "":
        joined_texts[0] = previous_entry_number
    else:
        # log an error here and break the program so that the document is not processed further
        print("note: log an error here and break the program so that the document is not processed any further")

    # print("joined_texts:", joined_texts)

    # Set flag for record_returned to False
    record_returned = False

    # Iterate through the elements from index 1 to 5 (inclusive)
    for element in joined_texts[1:]:
        if element != "":
            record_returned = True

    # Check if any non-empty element was found
    if record_returned:
        # Return joined_texts if any non-empty element was found
        return joined_texts
    else:
        # Return None if all elements are empty
        return None
    
def clean_image(image, response):
    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Iterate through the Textract response to identify LINE objects and draw their bounding boxes in white
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            left = block['Geometry']['BoundingBox']['Left'] * image.width
            top = block['Geometry']['BoundingBox']['Top'] * image.height
            width = block['Geometry']['BoundingBox']['Width'] * image.width
            height = block['Geometry']['BoundingBox']['Height'] * image.height
            right = left + width
            bottom = top + height +6

            # Draw a white rectangle around the LINE object's bounding box
            draw.rectangle([left, top, right, bottom], fill="white")

    return image

def get_dark_pixels(image, threshold=128):
    """Gets the number of dark pixels in each row and column of the image"""

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Convert the image to grayscale
    gray_image = np.array(image.convert("L"))

    # Create a binary mask of dark pixels
    dark_pixels = gray_image < threshold

    # Sum the dark pixels along each row to get the counts
    dark_pixels_per_row = np.sum(dark_pixels, axis=1)
    dark_pixels_per_column = np.sum(dark_pixels, axis=0)

    # 'dark_pixel_counts' now contains the number of dark pixels for each row

    row_list = dark_pixels_per_row.tolist()
    column_list = dark_pixels_per_column.tolist()

    return row_list, column_list

def find_max_dark_pixel_column(start, end, list_num_of_dark_pixels, coordinates, check_rows):
    max_dark_pixels = 0
    max_dark_pixel_column_index = None

    for i in range(round(start), round(end)):
        if list_num_of_dark_pixels[i] > max_dark_pixels:
            max_dark_pixels = list_num_of_dark_pixels[i]
            max_dark_pixel_column_index = i

    if check_rows:

        # Check if it's the last interval and the number of dark pixels is below 800
        if max_dark_pixel_column_index is not None and end == coordinates[-1] and max_dark_pixels < 800:
            # Set the highest row of pixels (lower border of the image) as the index
            max_dark_pixel_column_index = len(list_num_of_dark_pixels) - 1

    return max_dark_pixel_column_index

def get_dividers(coordinates, list_num_of_dark_pixels, check_rows=False):
    # Iterate through the intervals between x_coordinates
    interval_indices_relative = []
    interval_indices_absolute = []

    for i in range(len(coordinates) - 1):
        start = coordinates[i]
        end = coordinates[i + 1]
        max_dark_pixel_column_index = find_max_dark_pixel_column(start, end, list_num_of_dark_pixels, coordinates, check_rows)
        print("start, end: ", start, end)
        print(max_dark_pixel_column_index)
        interval_indices_absolute.append(max_dark_pixel_column_index)
        relative_max_dark_pixel_column_index = max_dark_pixel_column_index / len(list_num_of_dark_pixels)
        interval_indices_relative.append(relative_max_dark_pixel_column_index)
    
    return interval_indices_relative, interval_indices_absolute
