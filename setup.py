import json
import sys
import threading
import time

import cv2
import serial

from services import send_json
from vc.detector import print_timestamp


class aConnection(threading.Thread):
    def __init__(self, __conf, data, ims, wn):
        threading.Thread.__init__(self)
        self.conf = __conf
        self.data = data
        self._ims = ims
        self._wn = wn

    def run(self) -> None:
        _conf = self.conf
        arduino_conf = _conf["ARDUINO_CONFIGURATION"]
        auto_send = arduino_conf['auto_send']
        keep_connection = arduino_conf['keep_connection']
        port = arduino_conf['conf']['port']
        baudrate = arduino_conf['conf']['baudrate']
        timeout = arduino_conf['conf']['timeout']
        if auto_send is False:
            user_input = input(f"\n\tSend data to arduino at {port},\t YES \\ NO")
            if user_input == "YES":
                auto_send = True
            else:
                return
        print("auto_send: ", auto_send)
        if auto_send is True:
            arduino_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE
            )
            try:
                print_timestamp(f"\n Sending data to arduino at::\n\tport:: {port}\n\tbaudrate:: {baudrate}\n"
                                f"\ttimeout:: {timeout}\n", 0, 1)
                send_json(connection=arduino_connection, data=self.data, read=False)

                if keep_connection is True:
                    while True:
                        if arduino_connection.isOpen():
                            data = arduino_connection.readline().decode("utf-8")
                            if len(data) > 0:
                                # print(type(data))
                                i = None
                                if data.strip() == '--end--':
                                    print_timestamp(f"\n\tConnection made at: ", 0, 1)
                                elif data.strip() == '__loop_ended__':
                                    print_timestamp(f"{data} hence terminating thread", 0, 1)
                                    arduino_connection.close()
                                    cv2.destroyAllWindows()
                                    break
                                # elif data.strip() == "lane_1.jpg":
                                #     i = re_select(0, self._ims)
                                # elif data.strip() == "lane_2.jpg":
                                #     i = re_select(1, self._ims)
                                # elif data.strip() == "lane_3.jpg":
                                #     i = re_select(2, self._ims)
                                # elif data.strip() == "lane_4.jpg":
                                #     i = re_select(2, self._ims)
                                # else:
                                #     print("\narduino:: ", data)
                                # if i is not None:
                                #     try:
                                #         cv2.destroyAllWindows()
                                #         display_on_pc(self._wn, i)
                                #     except Exception as e:
                                #         sys.stderr.write(str(e))
                                else:
                                    print("\narduino:: ", data)
                            time.sleep(1)
            except serial.SerialException as s:
                sys.stderr.write(str(s))
            finally:
                arduino_connection.close()


def communicate_with_arduino(conf, data, ims, wn):
    """
    Responsible for serial communication between python code and microcontroller(arduino)
    :param wn:
    :param ims:
    :param conf:
    :param data:
    :return: _connection: Thread
    """
    _connection = None
    try:
        print("\nInitializing connection with microcontroller...")
        _connection = aConnection(conf, data, ims, wn)
        _connection.start()
        # connection.join()
        print("Connection made successfully...")
    except Exception as e:
        print("Something happened with sending data to arduino")
        sys.stderr.write(str(e))
    return _connection


def display_on_pc(window_name, image):
    """
    Responsible for displaying processed image on computer screen
    :param window_name:
    :param image:
    :return: None
    """
    print("\nStarting image thread...")
    try:
        # cv2.namedWindow(wn, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(wn, 1360, 600)
        cv2.startWindowThread()
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.imshow(window_name, image)  # Displaying the processed images
        cv2.waitKey(0)
        # while True:
        #     key = cv2.waitKey(0)
        #     if key == 27:
        #         print('esc is pressed closing all windows')
        #         cv2.destroyAllWindows()
        #         break
    except Exception as e:
        sys.stderr.write(str(e))  # propagating the error to the standard error handler
        cv2.destroyAllWindows()  # closing any cv2 window if exist


def load_conf(file_path='conf.json'):
    """
    Responsible for loading configuration from config file
    :param file_path:
    :return: configuration: json: dic
    """
    try:
        with open(file_path, "r") as f:
            print(f"Loading configuration from {f.name}")
            conf = json.loads(f.read())
            print(dict(conf))
            return conf
    except (FileNotFoundError, json.JSONDecodeError) as e:
        sys.stderr.write(e)
        exit(1)
