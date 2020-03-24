import subprocess
import json
import os

def read_json(file_path: str):
    json_file = open(file_path, 'r')
    return json.load(json_file)

def run_script(args, out =subprocess.PIPE, err =subprocess.PIPE):
    print(args)
    subprocess.Popen(args, stdout=subprocess.PIPE)


def run_script2(args  , timeout  = None, shell  = False, out=None)  :

    FNULL = open(os.devnull, 'w')

    process = subprocess.run(args, timeout=timeout, check=True, stdout=FNULL, stderr=FNULL, shell=shell)

    if process.returncode != 0:
        raise ScriptError(str(process))

    return process    
