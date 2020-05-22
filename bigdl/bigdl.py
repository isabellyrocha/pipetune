from utils import utils, energy
from pathlib import Path
import random
import time
import sys
from utils.Profiler import Profiler

class BigDL(object):

    def __init__(self):
        self._job_id = 0
        self._profiler = Profiler()

    def get_new_id(self):
        time.sleep(random.randrange(15))
        self._job_id =+ 1
        #print(self._job_id)
        return self._job_id


    def submit_v2(self, config, output):
        epochs = {1: "1", 2: "2", 3: "4"}
        cores = "1"
        number_of_epochs = int(config['end_trigger_num'])
        duration = sys.maxsize
        min_energy = sys.maxsize
        config['end_trigger_num'] = "1"
 #   file_path = open(file_name, 'r')
        for epoch in epochs.keys():
            #start = utils.timestamp()
            config['total_executor_cores'] = epochs[epoch]
            app = self.submit(config, output)
            start = utils.timestamp()
            app.wait()
            #utils.setCores(epochs[epoch])
            finish = utils.timestamp()
            epoch_duration = finish - start
            epoch_energy = energy.pdu_energy(start,finish)
            if epoch_energy < min_energy:
            #if epoch_duration < duration:
                min_energy = epoch_energy
                duration = epoch_duration
                cores = epochs[epoch]
        config['total_executor_cores'] = cores
        config['end_trigger_num'] = str(number_of_epochs-3)
        app = self.submit(config, output)
        app.wait()
 
    def submit_textclassifier(self, config, output):
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
            '--model', config['model'],
            '--batchSize', config['batchSize'],
            '--learning_rate', config['learning_rate'],
            '--embedding_dim', config['embedding_dim'],
            '--max_epoch', config['max_epoch']], output)

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
            '--batchSize', config['batch_size'],
            '--learningRate', config['learning_rate'],
            '--learningrateDecay', config['learning_rate_decay'],
            '--endTriggerNum', config['end_trigger_num']], output)

    def get_epoch_info(self,output_file):
        start  = 0
        finish = 0
        accuracy = 0
        with open(output_file, "r") as output:
            line = output.readline()
            while line:
                if "Epoch 1" in line and start == 0:
                    start  = utils.str_to_tstp(line.split(" INFO ")[0])
                if "accuracy" in line:
                    finish = utils.str_to_tstp(line.split(" INFO ")[0])
                    accuracy = line.split("accuracy: ")[1].replace(')','')
                    break
                line = output.readline()
        duration = finish - start
        cluster_energy = energy.pdu_energy(start, finish)
        info = {}
        info['accuracy'] = float(accuracy)
        info['energy'] = cluster_energy
        info['duration'] = duration
        info['ratio'] = 1#1#1#1#1#1#1#1#1#1#1#float(accuracy)/float(cluster_energy)
        return info

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
        cluster_energy = energy.pcm_energy(start, finish)
        info = {}
        info['accuracy'] = float(accuracy)
        info['energy'] = cluster_energy
        info['duration'] = duration
        info['ratio'] = float(accuracy)/float(cluster_energy)
        return info

    def run_mnist(self, 
                  config_file ="%s/pipetune/bigdl/config/mnist.json" % Path.home(),
                  total_executor_cores ="1",
                  memory ="2",
                  batch_size ="1024",
                  learning_rate ="0.01",
                  learning_rate_decay ="0.002",
                  epochs ="1",
                  info_in ={}):
        output_file ="%s/bigdl_logs/mnist_%s.log" % (Path.home(), str(time.time()))
        config = utils.read_json(config_file)
        config['total_executor_cores'] = total_executor_cores
        config['memory'] = "%sG" % memory
        config['batch_size'] = batch_size
        #print(config['batch_size'])
        config['learning_rate'] = learning_rate
        config['learning_rate_decay'] = learning_rate_decay
        config['end_trigger_num'] = epochs
        output = open(output_file, "w+")
        app = self.submit(config, output)
        app.wait()
        #self.submit_v2(config, output)
        output.close()
        info = self.get_epoch_info(output_file)
        if 'cores 'not in info:
            info['cores'] = {}
        info['cores'][total_executor_cores] = info['duration']
#        print(config)
        print(info)
        return info

    def run_mnist_off(self,
                  config_file ="%s/pipetune/bigdl/config/mnist.json" % Path.home(),
                  total_executor_cores ="1",
                  memory ="2",
                  batch_size ="1024",
                  learning_rate ="0.01",
                  learning_rate_decay ="0.002",
                  epochs ="1"):
        output_file ="%s/bigdl_logs/mnist_%s.log" % (Path.home(), str(time.time()))
        config = utils.read_json(config_file)
        config['total_executor_cores'] = total_executor_cores
        config['executor_cores'] = str(int(int(total_executor_cores)/4))
        config['memory'] = "%sG" % memory
        config['batch_size'] = batch_size
        #print(config['batch_size'])
        config['learning_rate'] = learning_rate
        config['learning_rate_decay'] = learning_rate_decay
        config['end_trigger_num'] = epochs
        output = open(output_file, "w+")
        app = self.submit(config, output)
        time.sleep(30)
        self._profiler.startMeasuring("mnist_%s_%s_%s" % (batch_size, learning_rate, learning_rate_decay))
        app.wait()
        #self.submit_v2(config, output)
        output.close()
        self._profiler.stopMeasuring()
        info = self.get_epoch_info(output_file)
        #if 'cores 'not in info:
        #    info['cores'] = {}
        #info['cores'][total_executor_cores] = info['duration']
#        print(config)
        print(info)
        return info


    def run_textclassifier(self,
                           config_file ="%s/pipetune/bigdl/config/textclassifier.json" %  Path.home(),
                           total_executor_cores ="1",
                           memory ="32",
                           model ="cnn",
                           batchSize ="128",
                           embedding_dim ="200",
                           learning_rate ="0.05",
                           max_epochs ="1",
                           info_in ={}):
        output_file ="%s/pipetune/bigdl/logs/textclassifier_%s.log" % (Path.home(), str(time.time()))
        config = utils.read_json(config_file)
        config['total_executor_cores'] = total_executor_cores
        config['model'] = model
        config['executor_memory'] = "%sG" % memory
        config['batchSize'] = batchSize
        config['learning_rate'] = learning_rate
        config['embedding_dim'] = embedding_dim
        config['max_epoch'] = max_epochs
        output = open(output_file, "w+")
        app = self.submit_textclassifier(config, output)
        app.wait()
        output.close()
        info = self.get_epoch_info(output_file, info_in)
        print(info)
        return info
