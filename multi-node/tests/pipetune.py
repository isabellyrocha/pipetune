from bigdl.bigdl import BigDL
from tune import textclassifier_hyperband as tune
from utils import utils, energy

if __name__ == '__main__':
    b = BigDL()
    #output_file = open("mnist.log", "w")
    #print(b.run_mnist(total_executor_cores="4", batch_size="32"))
    start = utils.timestamp()
    print("starting at %d" % start)
    #tune.runParameter()
    utils.start_perf()
    #tune.runPipetune()
    b.run_textclassifier(total_executor_cores = "16",
                                      model = "lstm",
                                      memory = "32",
                                      batchSize = "256",
                                      embedding_dim = "200",
                                      learning_rate = "0.005",
                                      max_epochs = "1")
    finish = utils.timestamp()
    utils.stop_perf()
    print("finishing at %d" % finish)
    print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pdu_energy(start,finish)))
