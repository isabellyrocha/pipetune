from bigdl.BigDL import BigDL
#from tune import off_mnist_tune_v1 as tune_v1
#from tune import off_mnist_tune_v2 as tune_v2
#from tune import off_mnist_pipetune as pipetune
#from tune import off_cnn_news20_tune_v1 as tune_v1
from tune import off_cnn_news20_tune_v2 as tune_v2
from tune import lenet5_pipetune as pipetune
from utils import utils, energy

if __name__ == '__main__':
#    for i in [0, 1, 2]:
#        print(i)
#        try:
#            start = utils.timestamp()
#            print("Starting at %d" % start)
#            tune_v1.runParameter()
#            finish = utils.timestamp()
#            print("Finishing at %d" % finish)
#            print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pdu_energy(start,finish)))
            start = utils.timestamp()
            print("Starting at %d" % start)
            pipetune.runParameter()
            finish = utils.timestamp()
            print("Finishing at %d" % finish)
            print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pdu_energy(start,finish)))
#            start = utils.timestamp()
#            print("Starting at %d" % start)
#            tune_v2.runParameter()
#            finish = utils.timestamp()
#            print("Finishing at %d" % finish)
#            print("Duration: %d\nEnergy: %d" % ((finish-start), energy.pdu_energy(start,finish)))
#        except Exception:
#            print("error")
