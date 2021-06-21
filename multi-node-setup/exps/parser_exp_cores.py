

with open('restuls.out') as fp:
    line = fp.readline()
    while line:
        sline = line.split(',')
        cores = sline[0]
        batch = int(sline[1])
        duration = int(sline[2])
        energy = int(sline[3])
        accuracy = float(sline[4])
        if batch == 32:
            duration_baseline = duration
            energy_baseline = energy
            accuracy_baseline = accuracy
        else:
            duration_diff = (duration-duration_baseline)/duration_baseline
            energy_diff = (energy-energy_baseline)/energy_baseline
            accuracy_diff = (accuracy-accuracy_baseline)/accuracy_baseline
            print("%d,%f,%f,%f" % (batch,accuracy_diff,duration_diff,energy_diff))
        line = fp.readline()
