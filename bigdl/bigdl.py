from utils import utils, energy
from pathlib import Path

class BigDL:
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

    def get_accuracy(self, output_file):
        with open(output_file, "r") as output:
            line = output.readline()
            while line:
                if "accuracy" in line:
                    accuracy = line.split("accuracy: ")[1].replace(')','')
                line = output.readline()
        return float(accuracy)

    def run_mnist(self, 
                  config_file ="%s/pipetune/bigdl/config/mnist.json" % str(Path.home()),
                  total_executor_cores =1,
                  output_file ="%s/pipetune/bigdl/logs/mnist.log" % str(Path.home())):
        config = utils.read_json(config_file, 4)
        output = open(output_file, "w")
        start = utils.timestamp()
        app = self.submit(config, output)
        app.wait()
        end = utils.timestamp()
        output.close()
        accuracy = self.get_accuracy(output_file)
        return {'accuracy': accuracy, 'duration': (end-start), 'energy': energy.pdu_energy(start, end)}
