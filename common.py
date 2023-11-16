import json

import psutil


PHI = (1+5**0.5)/2 

def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def write_str(path, txt):
    with open(path, 'wt', encoding='utf-8') as f:
        f.write(txt)

def write_process_info(process_data_path, process):
    process_psu = psutil.Process(process.pid)
    with process_psu.oneshot():
        process_data = {
            'PID': process.pid,
            'PPID': process_psu.ppid(),
            'NAME': process_psu.name(),
            'CMDLINE': process_psu.cmdline(),
            'CREATE_TIME': process_psu.create_time(),
            'EXE': process_psu.exe(),
            'CWD': process_psu.cwd(),
        }
    write_json(process_data_path, process_data)
