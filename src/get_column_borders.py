
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