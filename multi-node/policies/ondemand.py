import subprocess
import threading
from datetime import datetime
import time
import json
import sys
import os

filePath = ""
low_frequency = '2.0GHz'
high_frequency = '4.0GHz'
threshold = 1
hosts = ['eiger-1.maas', "eiger-2.maas", "eiger-3.maas", "eiger-4.maas"]
tasks = {}
full_sprinting = True

def setFrequency(host, frequency):
    COMMAND= "sudo cpupower frequency-set -u "+frequency+" -d "+frequency
    print("sprinting "+host+ " to "+frequency)
    ssh = subprocess.Popen(["ssh", host, COMMAND],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    #print(result)
    if result == []:
        error = ssh.stderr.readlines()
        print("Error in setFrequency!")
        print(error)

def isSprinting(host):
    COMMAND= "cpupower frequency-info"
    ssh = subprocess.Popen(["ssh", host, COMMAND],
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    print(result[11])
    if ("2.00 GHz" in str(result[11])):
        print(host+" is no sprinting")
        return False
    return True #('GHz' in str(result[11]))

def hasSprintingTasks(host):
    for task_id in list(tasks):
        task = tasks[task_id]
        if task['Host'] == host and 'Sprinting' in list(task):
            print("Host "+host+" has sprinting tasks")
            return True
    print("Host "+host+" does not have sprinting tasks")
    return False

def tasksMonitor(filePath):
    while os.path.exists(filePath):
        for task_id in list(tasks):
            try:
                if task_id in list(tasks):
                    task = tasks[task_id]
                    launch_time = task['Launch Time']/1000
                    now = datetime.timestamp(datetime.now())
                    if ((now - launch_time) > threshold) and (not isSprinting(task['Host'])):
                        tasks[task_id]['Sprinting'] = True
                        print("Sprinting host " + task['Host'] + " for task "+str(task_id))
                        setFrequency(task['Host'], high_frequency)
            except Exception as e:
                print("Error in taskMonitor:")
                print(e)

def deleteTask(task_id):
    host = tasks[task_id]['Host']
    del tasks[task_id]
    print("Deleted task " + str(task_id))
    if isSprinting(host) and (not hasSprintingTasks(host)):
        setFrequency(host, low_frequency)

def logParser(filePath):
    while os.path.exists(filePath):
        f = open(filePath)
        while os.path.exists(filePath):
            line = f.readline()
            if not line:
                print("Waiting for new line...")
                time.sleep(1)
            else:
                try:
                    jline = json.loads(line)
                    if jline['Event'] == 'SparkListenerTaskStart':
                        task_info = jline['Task Info']
                        tasks[task_info['Task ID']] = {
                            'Launch Time': task_info['Launch Time'],
                            'Host': task_info['Host']
                        }
                        print("Starting task " + str(task_info['Task ID']))
                    elif jline['Event'] == 'SparkListenerTaskEnd':
                            #print("DELETE")
                            #print(jline['Task Info'])
                        task_id = jline['Task Info']['Task ID']
                        deleteTask(task_id)
                except Exception as e:
                    print("Error in logParse in logParser:")
                    print(e)

def logParserFullSprinting(filePath):
    app_nodes = []
    f = open(filePath)
    line = f.readline()
    while len(app_nodes) < 2:
        #print(line)
        if line:
            jline = json.loads(line)
            if jline['Event'] == 'SparkListenerExecutorAdded':
                app_nodes.append(jline['Executor Info']['Host'])
        line = f.readline()
    for host in app_nodes:
        setFrequency(host, high_frequency)
    while os.path.exists(filePath):
        time.sleep(5)
    for host in app_nodes:
        setFrequency(host, low_frequency)

if full_sprinting:
    applications = []
    while True:
        for file_name in os.listdir("/home/ubuntu/spark-events"):
            if "inprogress" in file_name and file_name not in applications:
                filePath = "/home/ubuntu/spark-events/" + file_name
                print(filePath)
                monitor = threading.Thread(target=logParserFullSprinting, args=[filePath])
                monitor.start()
                applications.append(file_name)
        time.sleep(15)
else:
    applications = []
    while True:
        for file_name in os.listdir("/home/ubuntu/spark-events"):
            print(file_name in applications)
            if "inprogress" in file_name and file_name not in applications:
                filePath = "/home/ubuntu/spark-events/" + file_name
                print(filePath)
                monitor = threading.Thread(target=tasksMonitor, args=[filePath])
                parser = threading.Thread(target=logParser, args=[filePath])
                monitor.start()
                parser.start()
                applications.append(file_name)
        time.sleep(30)
