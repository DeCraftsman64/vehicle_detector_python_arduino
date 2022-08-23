import os.path
import time
from datetime import datetime

import cv2
import numpy as np


def is_similar(image1, image2):
    """
    Compares two images for similarities
    :param image1:
    :param image2:
    :return:  bool
    """
    return image1.shape == image2.shape and not (np.bitwise_xor(image1, image2).any())


_current_time = datetime.now()


# Printing with timestamp
def print_timestamp(threadName, delay, counter):
    """
    Prints the current timestamp with message provided
    :param threadName:
    :param delay:
    :param counter:
    :return: None
    """
    global _current_time
    while counter:
        delta = _current_time - datetime.now()
        time.sleep(delay)
        # time difference in milliseconds
        ms = -1 * delta.total_seconds() * 1000
        d = 'milliseconds'
        if ms > 10000:
            ms = -1 * delta.total_seconds()
            d = 'seconds'
        print("%s: %s : %f %s" % (threadName, time.ctime(time.time()), ms, d))
        counter -= 1
        # time difference in seconds
        # print(f"Time difference is {-1*delta.total_seconds()} seconds")
        _current_time = datetime.now()


class VehicleDetector:
    """
        Main Vehicle Detection Class
    """

    def __init__(self):
        # SetUp and Load Network
        net = cv2.dnn.readNet("dnn_model/yolov4.weights", "dnn_model/yolov4.cfg")
        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(size=(832, 832), scale=1 / 255)

        # Allow classes containing Vehicles only
        self.classes_allowed = [2, 3, 5, 6, 7]

    def detect_vehicles(self, img, nmsThreshold=0.3):
        """
        The function which detects the vehicles in an image
        :param img:
        :param nmsThreshold:
        :return: vehicle_boxes[]:
        """
        vehicles_boxes = []
        class_ids, scores, boxes = self.model.detect(img, nmsThreshold=nmsThreshold)
        for class_id, score, box in zip(class_ids, scores, boxes):
            if score < 0.5:
                # Skip detection with low confidence
                continue

            if class_id in self.classes_allowed:
                vehicles_boxes.append(box)

        vehicle_count = len(vehicles_boxes)  # Get vehicle count
        return vehicles_boxes, vehicle_count  # Return vehicle_boxes and vehicle count

    def append_boxes(self, img, vehicle_boxes, vehicle_count):
        """
        Render's boxes on image
        :param img:
        :param vehicle_boxes:
        :param vehicle_count:
        :return: None
        """
        for box in vehicle_boxes:
            x, y, w, h = box

            cv2.rectangle(img, (x, y), (x + w, y + h), (25, 0, 180), 3)

            cv2.putText(img, "Vehicle Count: " + str(vehicle_count), (20, 50), 5, 2, (100, 200, 0), 3)

        return None


# Image Class Wrapper
class Group:
    """ This is a wrapper for images with detect capabilities
    """

    # Class Setup
    def __init__(self, name, images=None):
        """
                Init method for Group
                :param name:
                :param images:
                :returns self
        """

        if images is None:
            images = np.array([], dtype=Image)
        self._images = images
        self._sorted_images = np.array([], dtype=Image)
        self.name = name
        self._img_data = {}

    def __repr__(self):
        return repr((self.name, len(self._images)))

    # Adds image to list
    def append_image(self, img):
        """
        appends image to Image List
        :param img:
        :return: (list , index)
        """
        self._images = np.append(self._images, [img])
        return self._images, len(self._images) - 1

    # Returns Image list
    def get_images(self):
        """
        Retrieves Image List
        :return: images[]
        """
        return self._images

    # Retrieves image at index
    def get_image(self, i):
        """
        Retrieves Image at index i
        :param i:
        :return: Image
        """
        return self._images[i]

    # Sorts Image List
    def sort(self, key=lambda image: image.get_vehicle_count(), reverse=False):
        """
        Returns the sorted and unsorted image list of the group
        :param key:
        :param reverse:
        :return:  sorted_images, unsorted_images
        """
        self._sorted_images = np.array(sorted(self._images, key=key, reverse=reverse))
        # print(self.__sorted_images)
        for i, img in enumerate(self._sorted_images):
            self._images[img.get_index()].set_position(i)
        return self._sorted_images, self._images

    def get_images_data(self):
        i_list, _ = self.sort(reverse=True)
        self._img_data["DATA"] = [
            {
                "PATH": img.name,
                "VEHICLE_COUNT": img.get_vehicle_count(),
                "INDEX": img.get_index(),
                "POSITION": img.get_position(),
            } for img in i_list
        ]
        self._img_data["COUNT"] = len(self._sorted_images)
        return self._img_data

    def serialise(self):
        return self.get_images_data()


# Image Class with extra properties
class Image(VehicleDetector):
    """ This is a modified Image Class with vehicle detection capabilities
        path, group :arg,
        Image :returns ,
        """

    def __init__(self, path, group: Group):
        super().__init__()
        self._name = os.path.basename(path)
        self.name = self._name
        self._path = path
        self.path = path
        self._img = cv2.resize(cv2.imread(path), (1200, 640))
        self._vehicle_boxes, self._vehicle_count = self.detect_vehicles(self._img)
        self._group = group
        _, self._index = self._group.append_image(img=self)
        self._position = None
        self._rendered = False

    def __repr__(self):
        return repr(self._path)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value != self._name:
            raise ValueError("Invalid action: Attribute Cannot Be Changed")
        self._name = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if value != self._path:
            raise ValueError("Invalid action: Attribute Cannot Be Changed")
        self._path = value

    def set_img(self, img):
        self._img = img

    def is_rendered(self, state=None):
        if state:
            self._rendered = state
        return self._rendered

    def set_position(self, pos: int):
        """
        Sets image position in group
        :param pos:
        :return: None
        """
        self._position = pos

    def get_position(self):
        """
        Returns position in group
        :return: position: int
        """
        return self._position

    def get_index(self):
        """
        Returns image index in group
        :return: index : int
        """
        return self._index

    def get_details(self):
        """
               Returns image index and position in group
               :return: index: int, position: int
               """
        return self._index, self._position

    def get_img(self):
        """
         Returns actual image
        :return: image
        """
        return self._img

    def get_vehicle_boxes(self):
        """
        Returns vehicle boxes
        :return: box[]
        """
        return self._vehicle_boxes

    def get_vehicle_count(self):
        """
        Returns vehicle count
        :return: count: int
        """
        return self._vehicle_count

    def get_group(self):
        """
        Returns Image wrapper
        :return: group: Group
        """
        return self._group

    def rescan(self):
        """
        Rescans the image for vehicles
        :return: None
        """
        self._vehicle_boxes, self._vehicle_count = self.detect_vehicles(self._img, nmsThreshold=0.3)

    def append_boxes(self, **kwargs):
        """
        appends box to the vehicle box list
        :param kwargs:
        :return: None
        """
        return super(Image, self).append_boxes(self._img, self._vehicle_boxes, self._vehicle_count)

    def is_similar(self, image2):
        """
        Compare image to self
        :param image2:
        :return: bool
        """
        return is_similar(self._img, image2)
