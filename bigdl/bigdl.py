from sprinting.utils import utils

class BigDL():

    def submit(config):
        return run_script([
            'spark-submit',
            '--master', config.master,
            '--driver-memory', config.driver_memory,
            '--total-executor-cores', config.total_executor_cores,
            '--executor-cores', config.executor_cores,
            '--executor-memory', config.executor_memory,
            '--py-files', config.py_files,
            '--properties-file', config.properties_file,
            '--jars', config.jars,
            '--conf', 'spark.driver.extraClassPath=/home/ubuntu/bigdl/lib/bigdl-SPARK_2.4-0.8.0-jar-with-dependencies.jar',
            '--conf', config.conf,
            '--appName', config.app_name,
            '--action', config.train,
            '--dataPath', config.data_path,
            '--batchSize', config.batch_size,
            '--learningRate', config.learning_rate,
            '--learningrateDecay', config.learning_rate_decay,
            '--endTriggerNum', config.end_trigger_num])

    def run_mnist():
        config = utils.read_json("apps/mnist.json")
        print(config)

if __name__ == '__main__':
    b = BigDL()
    b.run_mnist()
