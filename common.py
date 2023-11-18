import json
import os

import psutil


PHI = (1+5**0.5)/2 

def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def read_str(path):
    with open(path, 'rt', encoding='utf-8') as f:
        return f.read()

def write_str(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wt', encoding='utf-8') as f:
        f.write(txt)

def write_process_info(process_data_path, process):
    os.makedirs(os.path.dirname(process_data_path), exist_ok=True)
    process_data = get_process_data(process.pid)
    write_json(process_data_path, process_data)

def get_process_data(process_pid):
    process_psu = psutil.Process(process_pid)
    with process_psu.oneshot():
        process_data = {
            'PID': process_pid,
            'PPID': process_psu.ppid(),
            'NAME': process_psu.name(),
            'CMDLINE': process_psu.cmdline(),
            'CREATE_TIME': process_psu.create_time(),
            'EXE': process_psu.exe(),
            'CWD': process_psu.cwd(),
        }
    return process_data
