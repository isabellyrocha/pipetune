
duration_baseline = {}
energy_baseline = {}
accuracy_baseline = {}
with open('cores_results.out') as fp:
    line = fp.readline()
    while line:
        sline = line.split(',')
        cores = int(sline[0])
        batch = int(sline[1])
        duration = int(sline[2])
        energy = int(sline[3])
        accuracy = float(sline[4])
        if cores == 1:
            duration_baseline[batch] = duration
            energy_baseline[batch] = energy
            accuracy_baseline[batch] = accuracy
        else:
            duration_diff = (duration-duration_baseline[batch])/duration_baseline[batch]
            energy_diff = (energy-energy_baseline[batch])/energy_baseline[batch]
            accuracy_diff = (accuracy-accuracy_baseline[batch])/accuracy_baseline[batch]
            print("%d,%d,%f,%f,%f" % (cores,batch,accuracy_diff,duration_diff,energy_diff))
        line = fp.readline()
