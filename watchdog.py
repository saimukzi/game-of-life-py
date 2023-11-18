# Run on schedule
#   - Check GOL status
#   - Check OBS status
#   - Check streaming status # TODO

import argparse
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
ENABLE_REBOOT = config.get('ENABLE_REBOOT', False)

logging.basicConfig(
    filename=os.path.join(WORK_PATH, f'watchdog.{NOW_YYYYMMDD}.log'),
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)

logging.info(f'Watchdog start: NOW={NOW}')

if not config.get('ENABLE', True):
    logging.info('Watchdog disabled')
    exit()

# check watchdog start-end time
try:
    for _hglgyfpapj in range(1):
        watchdog_start_timestamp_path = os.path.join(WORK_PATH, 'watchdog_start_timestamp.txt')
        watchdog_start_timestamp = float(common.read_str(watchdog_start_timestamp_path))
        watchdog_end_timestamp_path = os.path.join(WORK_PATH, 'watchdog_end_timestamp.txt')
        watchdog_end_timestamp = float(common.read_str(watchdog_end_timestamp_path))
        if NOW - watchdog_start_timestamp >= 300:
            logging.info('Last watchdog start time is too old')
            break
        if watchdog_end_timestamp < watchdog_start_timestamp:
            logging.info('Another watchdog is running')
            exit()
except Exception as e:
    logging.exception(e)

# check log launch start time
try:
    launch_start_timestamp_path = os.path.join(WORK_PATH, 'launch_start_timestamp.txt')
    launch_start_timestamp = float(common.read_str(launch_start_timestamp_path))
    if NOW - launch_start_timestamp < 300:
        logging.info('Launch start time is too close')
        exit()
except Exception as e:
    logging.exception(e)

# check log launch end time
try:
    launch_end_timestamp_path = os.path.join(WORK_PATH, 'launch_end_timestamp.txt')
    launch_end_timestamp = float(common.read_str(launch_end_timestamp_path))
    if NOW - launch_end_timestamp < 300:
        logging.info('Launch end time is too close')
        exit()
except Exception as e:
    logging.exception(e)

good = False

try:
    # log watchdog start time
    watchdog_start_timestamp_path = os.path.join(WORK_PATH, 'watchdog_start_timestamp.txt')
    common.write_str(watchdog_start_timestamp_path, str(NOW))

    # check GOL
    gol_process_data_path = os.path.join(WORK_PATH, 'gol_process_data.json')
    gol_process_data = common.read_json(gol_process_data_path)
    gol_process_data0 = common.get_process_data(gol_process_data['PID'])
    if gol_process_data != gol_process_data0:
        logging.info('GOL process changed')
        raise Exception('GOL process changed')
    logging.info('GOL process check good')

    # check OBS
    obs_process_data_path = os.path.join(WORK_PATH, 'obs_process_data.json')
    obs_process_data = common.read_json(obs_process_data_path)
    obs_process_data0 = common.get_process_data(obs_process_data['PID'])
    if obs_process_data != obs_process_data0:
        logging.info('OBS process changed')
        raise Exception('OBS process changed')
    logging.info('OBS process check good')

    # log watchdog end time
    watchdog_end_timestamp_path = os.path.join(WORK_PATH, 'watchdog_end_timestamp.txt')
    common.write_str(watchdog_end_timestamp_path, str(NOW))

    good = True

except Exception as e:
    logging.exception(e)
    good = False

if good:
    logging.info('Watchdog good')
    sys.exit(0)

logging.info('Watchdog bad')

# kill GOL
try:
    logging.info('Kill GOL')
    gol_process_data_path = os.path.join(WORK_PATH, 'gol_process_data.json')
    gol_process_data = common.read_json(gol_process_data_path)
    gol_process_pid = gol_process_data['PID']
    gol_process = common.psutil.Process(gol_process_pid)
    gol_process.kill()
    gol_process.wait(timeout=30)
except Exception as e:
    logging.exception(e)

# kill OBS
try:
    logging.info('Kill OBS')
    obs_process_data_path = os.path.join(WORK_PATH, 'obs_process_data.json')
    obs_process_data = common.read_json(obs_process_data_path)
    obs_process_pid = obs_process_data['PID']
    obs_process = common.psutil.Process(obs_process_pid)
    obs_process.kill()
    obs_process.wait(timeout=30)
except Exception as e:
    logging.exception(e)

# restart windows
try:
    if ENABLE_REBOOT:
        logging.info('Restart Windows')
        os.system('shutdown /r /t 0')
    else:
        logging.info('Reboot disabled')
except Exception as e:
    logging.exception(e)
