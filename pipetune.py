from bigdl.bigdl import BigDL
from tune import mnist_hyperband as tune

if __name__ == '__main__':
    #b = BigDL()
    #output_file = open("mnist.log", "w")
    #print(b.run_mnist(total_executor_cores="4", batch_size="32"))
    tune.runParameter()
