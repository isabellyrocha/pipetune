import subprocess
import os
import time
from datetime import datetime

LOGS_PATH = "/home/ubuntu/perf/"
files = os.listdir(LOGS_PATH)

def str_to_tstp(time_str):
    return int(time.mktime(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timetuple()))

def month_converter(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    result = str(months.index(month) + 1)
    if len(result) < 2:
        result = "0%s" % result
    return result

#proc = subprocess.Popen(["ps", "-aux", "|", "grep", "spark.executor", "|", "grep", "root", "|", "awk", "'{print $2}'"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#out, err = proc.communicate()
#print(err)

def get_epoch(timestemp, epochs):
    nepochs= len(list(epochs.keys()))
#    print(epochs)
    for i in range(nepochs-1):
        if i == nepochs-2:
            next = "end"
        else:
            next = str(i+1)
#        print(i)
        if timestemp >= epochs[str(i)] and timestemp <= epochs[next]:
            return "%s,%d" % (i, (epochs[str(next)] - epochs[str(i)]))
#    return "%d,%d" % (nepochs-1,epochs[str(next)] - epochs[str(i)])

epochs = {}
with open('spark_filtered.log') as fp:
    line = fp.readline().strip()
    while line:
        (model, dataset, cores, memory, batch, log_id, epoch, timestemp) = line.split(",")
        #model = sline[0]
        #dataset = sline[1]
        #cores = sline[2]
        #memory = sline[3]
        #batch = sline[4]
        #log_id = sline[5]
        #epoch = sline[6]
        #timestemp = int(sline[7].strip())
        name = "%s_%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch, log_id)
        if name not in epochs:
            epochs[name] = {}
        epochs[name][epoch] = int(timestemp)
        line = fp.readline().strip()

for log_file in files:
    with open(LOGS_PATH + log_file) as fp:
        name = log_file.replace(".stat", "")
        log_id = name.split("_")[5]
        #curr_epochs = epochs[name]
        if log_id == "0":
            curr_epochs = epochs[name]
            if len(list(curr_epochs.keys())) > 5:
                line = fp.readline()
                sline = line.split(" ")
                sday = sline[5]
                smonth = month_converter(sline[4])
                syear = sline[7].strip()
                stime = sline[6]
                date_str = "%s-%s-%s %s" % (syear, smonth, sday, stime)
                start = str_to_tstp(date_str)
                line = fp.readline()
                line = fp.readline()
                while line:
                    sline = line.split(";")
                    current_time = int(float(sline[0].strip()) + start)
                    event = sline[3]
                    counts = sline[1]
                    epoch = get_epoch(current_time, epochs[name])
                    if epoch and epoch != "end":
                        if "not" in counts:
                            counts = "0"
                        print("%s,%s,%s,%s" % (name.replace("_",","), epoch, event, counts))
                    line = fp.readline()
