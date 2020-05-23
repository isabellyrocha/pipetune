from bigdl.bigdl import BigDL
from tune import off_mnist_tune_v2 as tune
from utils import utils, energy

if __name__ == '__main__':
    start = utils.timestamp()
    print("Starting at %d" % start)
    tune.runParameter()
    finish = utils.timestamp()
    print("Finishing at %d" % finish)
    print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pdu_energy(start,finish)))
