import subprocess
import json


class Utils:

    def read_json(file_path: str):
        json_file = open(file_path, 'r'):
        return json.load(json_file)

    def run_script(args, out =subprocess.PIPE, err =subprocess.PIPE):
        return subprocess.Popen(args, stdout=out, stderr=err)
