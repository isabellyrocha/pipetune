import time
from datetime import datetime
import os

LOGS_PATH = "/home/ubuntu/spark_logs/"
files = os.listdir(LOGS_PATH)

def str_to_tstp(time_str):
    return int(time.mktime(datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timetuple()))

#n_files = 0
for log_file in files:
#    n_files = n_files + 1
    (model, dataset, cores, memory, batch, log_id) = log_file.replace(".log", "").split("_")
    #model = slog[0]
    #dataset = slog[1]
    #cores = slog[2]
    #memory = slog[3]
    #batch = slog[4]
    #log_id = slog[5]
    if log_id == "0":
#        print(log_file)
        #n_files = n_files + 1 
        with open(LOGS_PATH + log_file) as fp:
            line = fp.readline()
            sline = line.split(" ")
            date = "%s %s" % (sline[0], sline[1])
            epoch = 0
            print("%s,%s,%s,%s,%s,%s,%d,%d" % (model, dataset, cores, memory, batch, log_id, epoch, str_to_tstp(date)))
            while line:
                if "[Epoch " in line:
                    sline = line.split(" ")
                    line_epoch = int(sline[7])
                    if line_epoch != epoch:
                        date = "%s %s" % (sline[0], sline[1])
                        epoch = line_epoch
                        print("%s,%s,%s,%s,%s,%s,%d,%d" % (model, dataset, cores, memory, batch, log_id, epoch, str_to_tstp(date)))
                line = fp.readline()
            date = "%s %s" % (sline[0], sline[1])
            print("%s,%s,%s,%s,%s,%s,end,%d" % (model, dataset, cores, memory, batch, log_id,  str_to_tstp(date)))

#print(n_files)
