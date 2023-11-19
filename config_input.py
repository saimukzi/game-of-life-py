import copy
import os

import common

MY_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

def get_config(config_path = None):
    if config_path is None:
        return get_config(os.path.join(MY_FOLDER_PATH, 'config.json'))

    CONFIG_FOLDER_PATH = os.path.dirname(config_path)

    my_config = common.read_json(config_path)
    ret_config = {}
    if 'IMPORT_LIST' in my_config:
        for import_path in my_config['IMPORT_LIST']:
            import_config = get_config(os.path.join(CONFIG_FOLDER_PATH, import_path))
            ret_config.update(import_config)

    for k,v in my_config.items():
        if k.endswith('_PATH'):
            my_config[k] = os.path.join(CONFIG_FOLDER_PATH, v)

    ret_config.update(my_config)

    return ret_config
