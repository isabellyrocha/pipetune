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
    return months.index(month) + 1

#proc = subprocess.Popen(["ps", "-aux", "|", "grep", "spark.executor", "|", "grep", "root", "|", "awk", "'{print $2}'"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#out, err = proc.communicate()
#print(err)

def get_epoch(timestemp, epochs):
    keys = list(epochs.keys())
#    print(epochs)
    for i in range(len(keys)-1):
        if i == len(keys)-2:
            next = "end"
        else:
            next = str(i+1)
#        print(i)
        if int(timestemp) >= int(epochs[str(i)]) and int(timestemp) <= int(epochs[next]):
            return str(i)
    return "10"

epochs = {}
with open('spark_filtered.log') as fp:
    line = fp.readline()
    while line:
        sline = line.split(",")
        log_id = sline[0]
        model = sline[1]
        dataset = sline[2]
        cores = sline[3]
        memory = sline[4]
        batch = sline[5]
        epoch = sline[6]
        timestemp = sline[7]
        name = "%s_%s_%s_%s_%s_%s" % (model, dataset, cores, memory, batch, log_id)
        if name not in epochs:
            epochs[name] = {}
        epochs[name][epoch] = int(timestemp.strip())
        line = fp.readline()

#print(epochs)
for log_file in files:
    with open(LOGS_PATH + log_file) as fp:
        name = log_file.replace(".stat", "")
#        print(name)
        line = fp.readline()
        sline = line.split(" ")
        sday = sline[5]
        smonth = month_converter(sline[4])
        syear = sline[7].strip()
        stime = sline[6]
        date_str = "%s-0%s-%s %s" % (syear, smonth, sday, stime)
#        print(date_str)
        start = str_to_tstp(date_str)
        line = fp.readline()
        #line = fp.readline()
        line = fp.readline()
        while line:
            sline = line.split(";")
            current_time = int(float(sline[0].strip()) + start)
            event = sline[3]
            counts = sline[1]
            #if "not" in value or int(value) != 0:
#            print(epochs[name])
            phase = get_epoch(current_time, epochs[name])
#            if int(phase) >=9:
            #print(phase)
            #events += counter + ","
            if phase != "end":
                if "not" in counts:
                    counts = "0"
                print("%s,%s,%s,%s" % (name.replace("_",","),event,phase,counts))
            line = fp.readline()
    #print(events)
