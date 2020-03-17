import sys
import numpy

NODES = [
    'eiger-1',
    'eiger-2',
    'eiger-3',
    'eiger-4'
    ]

TIMESTAMP = 0
NODE_NAME = 1
POWER = 2

filePath = sys.argv[1]
lowerBound = sys.argv[2]
upperBound = sys.argv[3]

def parseEnergy(file_path: str, lower_bound: float, upper_bound: float) -> float:
    nodes = {}
    for node in NODES:
        nodes[node] = []

    with open(file_path) as f:
        for line in f:
            sline = line.split(',')
            timestamp = sline[TIMESTAMP]
            #print(timestamp)
            if (timestamp != "timestamp" and sline[NODE_NAME] in NODES):
                if (upper_bound >= float(timestamp) >= lower_bound):
                    nodes[sline[NODE_NAME]].append(float(sline[POWER]))
                if (float(timestamp) > upper_bound):
                    break
    energy = 0
    for node in NODES:
        print("%s,%s" % (node, numpy.trapz(nodes[node])))
        energy += numpy.trapz(nodes[node])
    print("Total energy (Joules): %d" % energy)

parseEnergy("/home/ubuntu/power/power.out", float(lowerBound), float(upperBound))
