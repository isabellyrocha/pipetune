import subprocess
from datetime import datetime
import json
import os

def timestamp():
    return int(datetime.timestamp(datetime.now()))#datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def read_json(file_path:str, executors:int =1):
    with open(file_path, 'r') as json_file:
        json_obj = json.load(json_file)
    json_obj['total_executor_cores'] = str(executors)
    return json_obj

def run_script(args, out =subprocess.PIPE, err =subprocess.PIPE):
    return subprocess.Popen(args, stdout=out, stderr=err)
