from utils import utils, energy
from pathlib import Path
import random
import time
import sys
from utils.Profiler import Profiler
from utils.GroundTruth import GroundTruth

class BigDL(object):

    def __init__(self):
        self._profiler = Profiler()
        self._ground_truth = GroundTruth()

    def submit_v2(self, config, output):
        epochs = {1: "1", 2: "2", 3: "4"}
        cores = "1"
        number_of_epochs = int(config['end_trigger_num'])
        duration = sys.maxsize
        min_energy = sys.maxsize
        config['end_trigger_num'] = "1"
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


    def submit(self, config, output):
        command = ['spark-submit',
            '--master', config['master'],
            '--driver-memory', config['driver_memory'],
            '--total-executor-cores', config['total_executor_cores'],
            '--executor-cores', config['executor_cores'],
            '--executor-memory', config['executor_memory'],
            '--py-files', config['py_files'],
            '--properties-file', config['properties_file'],
            '--jars', config['jars'],
            '--conf', 'spark.driver.extraClassPath=/home/ubuntu/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar',
            '--conf', 'spark.executer.extraClassPath=bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar', config['conf']]
        for p in config['extras']:
            command.append("--%s" % p)
            command.append(config['extras'][p])
        print(command)
        return utils.run_script(command, output)

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
            '--conf', 'spark.driver.extraClassPath=/home/ubuntu/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar',
            '--conf', 'spark.executer.extraClassPath=bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar', config['conf'],
            '--model', config['model'],
            '--batchSize', config['batchSize'],
            '--learning_rate', config['learning_rate'],
            '--embedding_dim', config['embedding_dim'],
            '--max_epoch', config['max_epoch']], output)

    def submit_lenet5(self, config, output):
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
            '--conf', 'spark.driver.extraClassPath=/home/ubuntu/BigDL/dist/lib/bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar',
            '--conf', 'spark.executer.extraClassPath=bigdl-0.11.0-SNAPSHOT-jar-with-dependencies.jar', config['conf'],
            '--appName', config['app_name'],
            '--batchSize', config['batch_size'],
            '--learningRate', config['learning_rate'],
            '--learningrateDecay', config['learning_rate_decay'],
            '--endTriggerNum', config['end_trigger_num']], output)

    def get_epoch_info(self, output_file):
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
        info['ratio'] = 0
        if accuracy and cluster_energy:
            info['ratio'] = float(accuracy)/float(duration)
        return info

    def epoch_done(self, output_file):
        with open(output_file, "r") as output:
            line = output.readline()
            while line:
                if "Epoch 2" in line and not start:
                    return True
                line = output.readline()
        return False

    def get_info(self, output_file):
        start  = None
        finish = None
        accuracy = None
        with open(output_file, "r") as output:
            line = output.readline()
            while line:
                #print(line)
                if "Epoch 1" in line and not start:
                    print(line)
                    print(line.split(" INFO ")[0])
                    start  = utils.str_to_tstp(line.split(" INFO ")[0])
                    print(start)
                if "accuracy" in line:
                    print(line)
                    print(line.split(" INFO ")[0])
                    finish = utils.str_to_tstp(line.split(" INFO ")[0])
                    print(finish)
                    accuracy = line.split("accuracy: ")[1].replace(')','')
                line = output.readline()
        duration = 0
        if start and finish:
            duration = finish - start
        cluster_energy = energy.pdu_energy(start, finish)
        info = {}
        info['accuracy'] = float(accuracy)
        info['energy'] = cluster_energy
        info['duration'] = duration
        info['ratio'] = float(accuracy)/float(cluster_energy)
        return info

    def run_lenet5(self,
                  config_file ="%s/pipetune/bigdl/config/mnist.json" % Path.home(),
                  total_executor_cores ="1",
                  memory ="2",
                  batch_size ="1024",
                  learning_rate ="0.01",
                  learning_rate_decay ="0.002",
                  epochs ="1",
                  profile =False):
        output_file ="%s/bigdl_logs/mnist_%s.log" % (Path.home(), str(time.time()))
        config = utils.read_json(config_file)
        config['total_executor_cores'] = total_executor_cores
        config['executor_cores'] = str(int(int(total_executor_cores)/4))
        config['memory'] = "%sG" % memory
        config['batch_size'] = batch_size
        config['learning_rate'] = learning_rate
        config['learning_rate_decay'] = learning_rate_decay
        config['end_trigger_num'] = epochs
        output = open(output_file, "w+")
        app = self.submit_lenet5(config, output)
        #start = utils.timestamp()
        time.sleep(10)
        if profile:
            self._profiler.startMeasuring("mnist_%s_%s_%s" % (batch_size, learning_rate, learning_rate_decay), "eiger-2.maas")
        app.wait()
        #end = utils.timestamp()
        output.close()
        if profile:
            self._profiler.stopMeasuring("eiger-2.maas")
        info = self.get_info(output_file)
        print(info)
        return info

    def run_textclassifier_off(self,
                           config_file ="%s/pipetune/bigdl/config/textclassifier.json" %  Path.home(),
                           total_executor_cores ="1",
                           memory ="32",
                           model ="cnn",
                           batchSize ="128",
                           embedding_dim ="200",
                           learning_rate ="0.05",
                           max_epochs ="1",
                           profile =False):
        output_file ="%s/bigdl_logs/textclassifier_%s.log" % (Path.home(), str(time.time()))
        config = utils.read_json(config_file)
        config['total_executor_cores'] = total_executor_cores
        config['executor_cores'] = str(int(int(total_executor_cores)/4))
        config['model'] = model
        config['executor_memory'] = "%sG" % memory
        config['batchSize'] = batchSize
        config['learning_rate'] = learning_rate
        config['embedding_dim'] = embedding_dim
        config['max_epoch'] = max_epochs
        output = open(output_file, "w+")
        app = self.submit_textclassifier(config, output)
        time.sleep(60)
        if profile:
            self._profiler.startMeasuring("%s_news20_%s_%s_%s" % (model, batchSize, embedding_dim, learning_rate), "eiger-2.maas")
        if not self.epoch_done(output_file):
            time.sleep(60)
        if profile:
            self._profiler.stopMeasuring("eiger-2.maas")
        metrics = self._profiler.getMetrics("%s_news20_%s_%s_%s" % (model, batchSize, embedding_dim, learning_rate))
        (cores, memory) = self._ground_truth.getConfig(metrics, batchSize)
        utils.set_cores(cores)
        utils.set_mem(memory)
        app.wait()
        output.close()
        info = self.get_epoch_info(output_file)
        print(info)
        return info


    def run(self, config, profile =False):
        job_name = "job_%s" % str(time.time())
        output_file ="%s/bigdl_logs/%s.log" % (Path.home(), job_name)
        output = open(output_file, "w+")
        app = self.submit(config, output)
        #start = utils.timestamp()
        #time.sleep(5)
        if profile:
            self._profiler.startMeasuring(job_name, "eiger-2.maas")
        app.wait()
        #end = utils.timestamp()
        output.close()
        if profile:
            self._profiler.stopMeasuring("eiger-2.maas")
        info = self.get_info(output_file)
        print(info)
        return info
