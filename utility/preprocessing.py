import os
import cv2
import numpy as np
from PIL import Image
from os import listdir

# status code for centre_crop function
CROP_LENGTH_OUT_OF_IMG_BOUND = 1
CROP_LENGTH_OUT_OF_EYE_BOUND = 2
CROP_LENGTH_INSIDE_OF_EYE_BOUND = 3

def preprocess_images(src, partial_list, dst, clahe_channels, centre_crop, format, output_size = 512):
    # get all files in src
    try:
        img_paths = [src + '/' + x for x in listdir(src)]
    except:
        print('source path does not exist');
        return False

    # check if there is any image in src
    if (len(img_paths) == 0):
        print('No image exist in '+ src)
        return False

    # check if dst directory exist
    if (not os.path.exists(dst)):
        print('Destination path does not exist. Creating the path...')
        os.mkdir(dst)

    i = 0

    if partial_list == None:
        total_imgs = len(img_paths)
    else:
        total_imgs = len(partial_list)

    for img_path in img_paths:
        # get the image name and its extension
        img_name = os.path.basename(os.path.splitext(img_path)[0])
        img_extension = os.path.splitext(img_path)[1]

        # skip preprocessing if partial list is used
        if partial_list != None:
            if img_name not in partial_list:
                continue

        # start preprocessing
        print('preprocessing image {0} ({0}/{1})'.format(i+1, total_imgs))

        # read the image
        img = cv2.imread(img_path)

        # centre crop the image
        if (centre_crop):
            img = fit_crop(img)

		# resizing the image
        img = cv2.resize(img, (output_size, output_size)) # new_size should be in (width, height) format

        # CLAHE-ing
        img = clahe(img, clahe_channels)

        # convert image memory to array
        img = Image.fromarray(img)

        # save the final preprocessed image
        if (format == 0):
            img.save(dst + '/' + img_name + '.tiff')
        else:
            img.save(dst + '/' + img_name + '.jpeg')
        i += 1

    return True

def fit_crop(img):
    inner_length = 0
    outer_length = 5000
    middle_length = 0

    while (abs(outer_length - inner_length) > 5):
        middle_length = int((inner_length + outer_length)/2)
        crop_status = find_crop(img, middle_length)

        if (crop_status == CROP_LENGTH_OUT_OF_IMG_BOUND or crop_status == CROP_LENGTH_OUT_OF_EYE_BOUND):
            outer_length = middle_length
        else:
            inner_length = middle_length

    output_img = centre_crop(img, middle_length)

    return output_img

def find_crop(img, crop_length):
    img_width = img.shape[1]
    img_height = img.shape[0]

    if (crop_length > img_width or crop_length > img_height):
        return CROP_LENGTH_OUT_OF_IMG_BOUND

    starting_x = int((img_width - crop_length) / 2)
    starting_y = int((img_height - crop_length) / 2)

    if (img[starting_y][starting_x][0] < 15 and img[starting_y][starting_x][1] < 15 and img[starting_y][starting_x][2] < 15):
        return CROP_LENGTH_OUT_OF_EYE_BOUND
    else:
        return CROP_LENGTH_INSIDE_OF_EYE_BOUND

def centre_crop(img, crop_length):
    img_width = img.shape[1]
    img_height = img.shape[0]

    starting_x = int((img_width - crop_length) / 2)
    starting_y = int((img_height - crop_length) / 2)

    ending_x = starting_x + crop_length
    ending_y = starting_y + crop_length

    cropped_img = img[starting_y:ending_y, starting_x:ending_x, :]

    return cropped_img

def clahe(img, clahe_channels):
    # extract individual channel of the image (b, g, r)
    b_channel, g_channel, r_channel = cv2.split(img)

    # CLAHE-ing
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
    if 'R' in clahe_channels:
        r_channel = clahe.apply(r_channel)

    if 'G' in clahe_channels:
        g_channel = clahe.apply(g_channel)

    if 'B' in clahe_channels:
        b_channel = clahe.apply(b_channel)

    # merge all color channels
    output_img = cv2.merge([r_channel, g_channel, b_channel])

    return output_img
