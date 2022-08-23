# importing the modules needed to run the program

from services import process_images_with_conf
from setup import load_conf, communicate_with_arduino, display_on_pc
from vc.detector import Group

if __name__ == '__main__':
    # Loading configurations from config file
    conf = load_conf(file_path='conf.json')
    # Getting settings in configurations
    settings = conf['settings']
    # Processing images (Vehicle detection and rendering is included)
    print(conf['settings'])
    for i, (name, folder_conf) in enumerate(conf["FOLDER_DETAILS"].items()):
        group = Group(name)
        if folder_conf["run"]:
            (img, _images), wn, __conf = process_images_with_conf(grp=group, conf=folder_conf, i=i)
            # Checking if arduino communication is enabled(all values and conf are in the conf file)
            c_thread = None
            if settings['controller'] is True and __conf["send"]:
                c_thread = communicate_with_arduino(conf=conf, data=group.serialise(), ims=_images, wn=wn)
            # Checking if display is enabled
            if settings["monitor"] is True and __conf["show"] is True:
                display_on_pc(window_name=wn, image=img)
            # while c_thread and c_thread.is_alive():
            #     pass
            # else:
            #     break
    # Finally, exiting program
    exit(0)
