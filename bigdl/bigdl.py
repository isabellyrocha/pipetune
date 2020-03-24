from utils import utils
from pathlib import Path

class BigDL:
    def submit(self, config):
        print(config)
        #output_file = open("mnist.log", "w")
        return utils.run_script([
            '/usr/local/spark/bin/spark-submit',
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
            '--endTriggerNum', config['end_trigger_num']])

    def run_mnist(self, file ="%s/pipetune/bigdl/config/mnist.json" % str(Path.home())):
        config = utils.read_json(file)
        self.submit(config)
