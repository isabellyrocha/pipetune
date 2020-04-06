import subprocess
import time
from datetime import datetime
import json
import os

def str_to_tstp(time_str:str):
    return int(time.mktime(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timetuple()))

def timestamp():
    return int(datetime.timestamp(datetime.now()))#datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def read_json(file_path:str, executors:str ="1", batch_size:str ="1024"):
    with open(file_path, 'r') as json_file:
        json_obj = json.load(json_file)
    json_obj['total_executor_cores'] = executors
    json_obj['batch_size'] = batch_size
    return json_obj

def run_script(args, out =subprocess.PIPE, err =subprocess.PIPE):
    return subprocess.Popen(args, stdout=out, stderr=err)
