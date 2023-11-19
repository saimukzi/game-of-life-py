# Run when PC launch
#   - Start GOL
#   - Start OBS and start streaming

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
MY_PID = os.getpid()

# get config
config = config_input.get_config()
WORK_PATH = config['WORK_PATH']

os.makedirs(WORK_PATH, exist_ok=True)

if not config.get('ENABLE', True):
    exit()

# log launch start time
launch_start_timestamp_path = os.path.join(WORK_PATH, 'launch_start_timestamp.txt')
common.write_str(launch_start_timestamp_path, str(NOW))

# start GOL
python_exec = sys.executable
gol_process = subprocess.Popen([python_exec, os.path.join(MY_FOLDER_PATH, 'main.py')], env=os.environ.copy())
common.write_process_info(os.path.join(WORK_PATH, 'gol_process_data.json'), gol_process)

# start OBS
obs_process = subprocess.Popen([config['OBS_PATH'], '--minimize-to-tray', '--disable-shutdown-check'], cwd=os.path.dirname(config['OBS_PATH']), env=os.environ.copy())
common.write_process_info(os.path.join(WORK_PATH, 'obs_process_data.json'), obs_process)

# start streaming
cl = obs.ReqClient(host='localhost', port=config['OBS_WEBSOCKET_PORT'], password=config['OBS_WEBSOCKET_PASSWORD'], timeout=60)
cl.send(
    "SetStreamServiceSettings",
    data={
        'streamServiceSettings': {
            'bwtest': False,
            'key': config['STREAM_KEY'],
            'server': config['STREAM_RTMP_URL_0'],
            'use_auth': False
        },
        'streamServiceType': 'rtmp_custom'
    }
)
cl.send('StartStream')

# log launch end time
end_time = time.time()
launch_end_timestamp_path = os.path.join(WORK_PATH, 'launch_end_timestamp.txt')
common.write_str(launch_end_timestamp_path, str(end_time))
