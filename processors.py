import datetime
import glob
import pathlib
import re
from typing import List

import cv2
import numpy as np

from vc.detector import Image, Group, print_timestamp


# Function that scans the folder for images
def scan_folder(folder_path, group: Group, render=False):
    """
    Reads folder for images and detects the vehicles
    :param folder_path:
    :param group:
    :param render:
    :return: image[]: List[Image], group: Group
    """
    if pathlib.Path(folder_path).exists():
        images = np.array([], dtype=Image)  # Empty image list

        print_timestamp(f"Task 1a: scanning images in {folder_path}", 0, 1)
        images_folder = glob.glob(f"{folder_path}/*.jpg")  # scanning the folder for images with the jpeg extension
        images_folder.sort(key=lambda f: int(re.sub('\D', '', f)))
        print_timestamp(f"Task 1b: image scan 'jpeg' completed for {folder_path}... count={len(images_folder)}", 0, 1)
        print_timestamp(f"Task 2: reading images and detecting vehicles...", 0, 1)
        # images_folder.sort()

        # Looping over image path found in the images folder
        for i, img_path in enumerate(images_folder):
            # Getting the current system time
            t = datetime.datetime.now()
            print_timestamp(f"Task 2-{i}a: beginning detection for {img_path}....", 0, 1)
            img = Image(img_path, group)  # Loading the image as our Image Class
            print_timestamp(f"Task 2-{i}b: completed detection for {img.name}....", 0, 1)

            if render:
                print_timestamp(f"Task 3a: Rendering detection for {img_path}....", 0, 1)
                img.append_boxes()  # Rendering the boxes unto the processed image
                print_timestamp(f"Task 3b: Completed rendering for {img.name}....", 0, 1)

            # Getting the duration
            dt = t - datetime.datetime.now()
            run_time = -1 * dt.total_seconds()  # Converting into seconds

            images = np.append(images, [img])
            # images.append(img)  # Append image to Images list
            print("\n\t\t%s : %f seconds\n" % (images[i], run_time))  # Printing the duration
            # print('\a')

        return images, group  # Returning the Images List and the Group(wrapper) class
    else:
        raise NotADirectoryError(f"Please check {folder_path} in conf.json")


# Function that compares the vehicle counts of the images provided
def compare_all_images(images_folder, group: Group,
                       sort_images=False, render_boxes=True,
                       sort_key=lambda image: image.vehicle_count, reverse=False):
    """
    Renders sorted image according to scan comparison. A sort key must be provided
    :param images_folder:
    :param group:
    :param sort_images:
    :param render_boxes:
    :param sort_key:
    :param reverse:
    :return: image
    """
    __images, __group = scan_folder(images_folder, group, render_boxes)

    print_timestamp(f"Task 4a: Starting analyses on processed images....", 0, 1)

    # Getting the sorted and unsorted processed images from the Group
    p_sorted_images, p_unsorted_images = __group.sort(key=sort_key, reverse=reverse)

    # Selecting the format of according to  sort_images value
    processed_images = p_sorted_images if sort_images is True else p_unsorted_images

    print_timestamp(f"Sorted: {sort_images}, {processed_images} \n {p_unsorted_images}", 0, 1)

    # Getting position of the highest vehicle count image
    max_pos = processed_images.tolist().index(max(processed_images, key=sort_key))
    # Getting the mid-position of the images list
    mid_pos = int(len(processed_images.tolist()) / 2)

    s_img = processed_images[max_pos]  # Getting the image with the highest vehicle count
    print_timestamp(f"Task 4: Analyses on processed images completed....", 0, 1)

    print_timestamp(f"mid_pos: {mid_pos}, max_pos:{max_pos}", 0, 1)

    # Comparing Vehicle count for the two images and selecting the greatest count
    print_timestamp("Task 5: Rendering final result....", 0, 1)
    render_scan(s_img, processed_images)  # Rendering the final sorting
    print_timestamp("Task 5: Rendering completed....", 0, 1)

    print_timestamp("Task 6: Setting final image environment....", 0, 1)

    img = generate_img(processed_images=processed_images, mid_pos=mid_pos)

    return img, processed_images  # Return Final Processed


def re_select(i, images):
    img = images[i].get_img()
    # gray = cv2.cvtColor(img.get_img(), cv2.COLOR_BGR2GRAY)
    # path = "src/temp/" + img.name
    # cv2.imwrite(path, gray)
    # new_img = cv2.imread(path)
    # images[i].set_img(new_img)
    s_w, s_h, s_z = img.shape
    cv2.rectangle(img,
                  (0, 0),
                  (s_h, s_w - 5),
                  (255, 255, 255), 10)
    return generate_img(images, int(len(images.tolist()) / 2))


def generate_img(processed_images, mid_pos):
    print_timestamp("Task 7: Generating image....", 0, 1)
    print("\n\t", "P: ", processed_images, "\n")
    count = len(processed_images.tolist())
    # concatenate image Horizontally
    if count > 2:
        T = np.concatenate(tuple([img.get_img() for img in processed_images][:mid_pos]), axis=1)  # Top Row
        D = np.concatenate(tuple([img.get_img() for img in processed_images][mid_pos:]), axis=1)  # Bottom  Row
        # concatenate image Vertically
        V = np.concatenate((T, D), axis=0)  # Adding Rows (Top & Bottom)
    elif count == 2:
        V = np.concatenate((processed_images[0], processed_images[1]), axis=0)
    else:
        V = processed_images[0]
    print_timestamp("Task 8: Image generation completed! 100%....", 0, 1)

    print_timestamp("Task 9: Resizing generated image to 1360 * 600....", 0, 1)
    # Resizing final image
    img = cv2.resize(V, (1360, 600))

    print_timestamp("Task 10: Image processing completed...", 0, 1)

    return img


# Function that render's vehicle position and state unto the images
def render_scan(selected_image: Image, other_images: List[Image]):
    """
    Renders scan on image
    :param selected_image:
    :param other_images:
    :return: image
    """
    # Getting the actual image from our Image Class
    s_img = selected_image.get_img()
    # Getting the dimension of the selected image
    s_w, s_h, s_z = s_img.shape
    # Rendering the Outer Rectangle
    cv2.rectangle(s_img,
                  (0, 0),
                  (s_h, s_w - 5),
                  (0, 255, 0), 10)
    # Rendering Text
    cv2.putText(s_img,
                "Status: Go!",
                (int(20), int(s_h / 2)),
                5, 2,
                (100, 200, 0), 3)

    # Sorting other images
    for i, image in enumerate(other_images):
        img = image.get_img()
        w, h, z = img.shape

        if not selected_image.is_similar(img):
            cv2.rectangle(img,
                          (0, 0),
                          (h, w - 5),
                          (0, 0, 255),
                          10)
            cv2.putText(img,
                        "STATUS: Waiting...",
                        (int(20), int(h / 2)),
                        5, 2,
                        (0, 0, 255),
                        3)
        # Rendering Position
        cv2.putText(img,
                    "Lane: " + str(i + 1),
                    (w + 330, 50),
                    5, 2,
                    (25, 0, 255),
                    3)

        # cv2.putText(img,
        #             "img " + image.name,
        #             (int(w + 160), int(h / 2)),
        #             5, 2,
        #             (0, 0, 0),
        #             3)
