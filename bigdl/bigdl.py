from utils import utils, energy
from pathlib import Path
import random
import time

class BigDL(object):

    def __init__(self):
        self._job_id = 0

    def get_new_id(self):
        time.sleep(random.randrange(15))
        self._job_id =+ 1
        #print(self._job_id)
        return self._job_id

    def submit(self, config, output):
        return utils.run_script([
            'spark-submit',
            '--master', config['master'],
            '--driver-memory', config['driver_memory'],
            '--total-executor-cores', config['total_executor_cores'],
            '--executor-cores', config['executor_cores'],
            '--executor-memory', config['executor_memory'],
            '--py-files', config['py_files'],
            '--properties-file', config['properties_file'],
            '--jars', config['jars'],
            '--conf', 'spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar',
            '--conf', 'spark.executer.extraClassPath=bigdl-SPARK_2.4-0.8.0.jar', config['conf'],
            '--appName', config['app_name'],
            '--action', config['action'],
            '--dataPath', config['data_path'],
            '--batchSize', config['batch_size'],
            '--learningRate', config['learning_rate'],
            '--learningrateDecay', config['learning_rate_decay'],
            '--endTriggerNum', config['end_trigger_num']], output)

    def get_info(self, output_file):
        start  = None
        finish = None
        accuracy = None
        with open(output_file, "r") as output:
            line = output.readline()
            while line:
                if "Epoch 1" in line and not start:
                    start  = utils.str_to_tstp(line.split(" INFO ")[0])
                if "accuracy" in line:
                    finish = utils.str_to_tstp(line.split(" INFO ")[0])
                    accuracy = line.split("accuracy: ")[1].replace(')','')
                line = output.readline()
        duration = finish - start
        cluster_energy = energy.pdu_energy(start, finish)
        info = {}
        info['accuracy'] = float(accuracy)
        info['energy'] = cluster_energy
        info['duration'] = duration
        info['ratio'] = accuracy/duration
        return float(accuracy)

    def run_mnist(self, 
                  config_file ="%s/pipetune/bigdl/config/mnist.json" % Path.home(),
                  total_executor_cores ="1",
                  batch_size ="1024"):
        output_file ="%s/pipetune/bigdl/logs/mnist_%s.log" % (Path.home(), str(time.time()))
        config = utils.read_json(config_file, total_executor_cores, batch_size)
        output = open(output_file, "w")
        app = self.submit(config, output)
        app.wait()
        output.close()
        return self.get_info(output_file)
