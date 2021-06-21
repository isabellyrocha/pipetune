from bigdl.bigdl import BigDL
from tune import off_mnist_pipetune as lenet5
from tune import off_fashion_mnist_tune_v2 as fashion
from tune import off_cnn_news20_pipetune as news20
from utils import utils, energy
from numpy import random as random
import time

if __name__ == '__main__':
    x = random.poisson(lam=5000, size=10)
    print(x)
    system = [lenet5, news20]
    diff = 0
    for i in range(1):
        try:
            start = utils.timestamp()
            print("Starting at %d" % start)
            system[i%2].runParameter()
            finish = utils.timestamp()
            print("Finishing at %d" % finish)
            print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pdu_energy(start,finish)))
            diff = x[i] - (finish-start)
            print("Waiting time: %d" %  diff)
            if diff > 0:
                time.sleep(diff)
        except Exception:
            print("error")
