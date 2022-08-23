import json
import sys
import time

from serial import Serial

from processors import compare_all_images
from vc.detector import Group


# For sending data to arduino
def send_json(connection: Serial, data: dict, read=False):
    """
    Convert python dic to json
    :param connection:
    :param data:
    :param read:
    :return: None:
    :author: NKS
    """
    data = json.dumps(data)
    if connection.isOpen():
        time.sleep(2)
        msg = data.encode('ascii')
        connection.write(msg)
        time.sleep(2)
        connection.flush()
    else:
        sys.stderr.write("Opening error")
        return
    if read:
        try:
            time.sleep(3)
            incoming = connection.readline().decode("utf-8")
            print("Adds ", incoming)
        except Exception as e:
            sys.stderr.write(str(e))
    print(f"\nSending data successful: {data}")
    # time.sleep(1)
    # connection.close()


# Link between configuration and processors.py
def run(__path: str, __group: Group, __wn: str, sort=False, reverse=True, render_boxes=True, __conf=None):
    """
    Passes data to the processor module(processors.py)
    :param __path:
    :param __group:
    :param __wn:
    :param sort:
    :param reverse:
    :param render_boxes:
    :param __conf:
    :return: (img, images), __wn, __group, __conf
    """

    return compare_all_images(images_folder=__path, group=__group, sort_images=sort, render_boxes=render_boxes,
                              sort_key=lambda image: image.get_vehicle_count(),
                              # sorting images by their vehicle count
                              reverse=reverse), __wn, __conf


# Refer to the compare_all_images module in processors.py
def process_images_with_conf(conf, grp: Group, i=0):
    """
    Processes images with the given config using the processors' module(processors.py)
    NB (Parses configuration and send data to the run function)
    :param i:
    :param grp:
    :param conf:
    :return: (img, images), __wn, __group, __conf
    """
    return run(__path=conf['path'], __group=grp, __wn=f"__Vehicle Detection Module {i}__",
               sort=conf['sort'], reverse=conf['reverse'], render_boxes=conf['render_boxes'],
               __conf=conf["conf"])
