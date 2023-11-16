# Run on schedule
#   - Check GOL status
#   - Check OBS status
#   - Check streaming status # TODO

import logging
import time
import obsws_python as obs
import os
import subprocess
import sys

import common
import config_input

# const
MY_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
NOW = time.time()
NOW_YYYYMMDD = time.strftime('%Y%m%d', time.localtime(NOW))

# get config
config = config_input.get_config()
WORK_PATH = config['WORK_PATH']

logging.basicConfig(filename=os.path.join(WORK_PATH, f'watchdog.{NOW_YYYYMMDD}.log'))

logging.info('Watchdog start')

if not config.get('ENABLE', True):
    logging.info('Watchdog disabled')
    exit()

# check log launch start time
launch_start_timestamp_path = os.path.join(WORK_PATH, 'launch_start_timestamp.txt')
launch_start_timestamp = float(common.read_str(launch_start_timestamp_path))
if NOW - launch_start_timestamp < 300:
    logging.info('Launch start time is too close')
    exit()

# check log launch end time
launch_end_timestamp_path = os.path.join(WORK_PATH, 'launch_end_timestamp.txt')
launch_end_timestamp = float(common.read_str(launch_end_timestamp_path))
if NOW - launch_end_timestamp < 300:
    logging.info('Launch end time is too close')
    exit()

good = False

try:
    # check GOL
    gol_process_data_path = os.path.join(WORK_PATH, 'gol_process_data.json')
    gol_process_data = common.read_json(gol_process_data_path)
    gol_process_data0 = common.get_process_data(gol_process_data['PID'])
    if gol_process_data != gol_process_data0:
        logging.info('GOL process changed')
        raise Exception('GOL process changed')

    # check OBS
    obs_process_data_path = os.path.join(WORK_PATH, 'obs_process_data.json')
    obs_process_data = common.read_json(obs_process_data_path)
    obs_process_data0 = common.get_process_data(obs_process_data['PID'])
    if obs_process_data != obs_process_data0:
        logging.info('OBS process changed')
        raise Exception('OBS process changed')

    good = True

except Exception as e:
    logging.error(e)
    good = False
