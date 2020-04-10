from bigdl.bigdl import BigDL
from tune import mnist_hyperband as tune
from utils import utils, energy

if __name__ == '__main__':
    #b = BigDL()
    #output_file = open("mnist.log", "w")
    #print(b.run_mnist(total_executor_cores="4", batch_size="32"))
    start = utils.timestamp()
    print("starting at %d" % start)
    tune.runParameter()
    finish = utils.timestamp()
    print("finishing at %d" % finish)
    print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pcm_energy(start,finish)))
