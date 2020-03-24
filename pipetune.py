from bigdl.bigdl import BigDL

if __name__ == '__main__':
    b = BigDL()
    output_file = open("mnist.log", "w")
    print(b.run_mnist())
