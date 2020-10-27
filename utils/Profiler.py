from influxdb import InfluxDBClient
from numpy import mean
from pandas import DataFrame
import subprocess
from paramiko import SSHClient
from scp import SCPClient
from pathlib import Path

home = str(Path.home())

class Profiler():

    def __init__(self, nodes):
#        self.influx_client = InfluxDBClient(args.influx_host, args.influx_port, args.influx_user, args.influx_pass, args.influx_database)
        self.influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'profiler')
        self._nodes = nodes

    def write_event(self, measurement: str, tags: dict, timestemp, value: int):
        json_body = [
        {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": {
                "value": value
            }
        }]
        self.influx_client.write_points(json_body)

    def startMeasuring(self, file_name, node_name):
        #file_name = "lenet_%s_%s_%s_%s_%d" % (dataset, total_executor_cores, memory, batch_size, trial_id)
        return subprocess.Popen(["ssh", node_name, "bash", "%s/pipetune/scripts/perf/start-perf.sh" % home, "%s/perf/%s" % (home, file_name)])

    def stopMeasuring(self, node_name):
        return subprocess.Popen(["ssh", node_name, "bash", "%s/pipetune/scripts/perf/stop-perf.sh" % home])

    def getMetrics(self, file_name):
        copy = subprocess.Popen("scp %s:perf/%s.stat %s/perf" % (self._nodes[0], file_name, home), shell=True)
        copy.wait()
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(self._nodes[0])
        with SCPClient(ssh.get_transport()) as scp:
#    scp.put('test.txt', 'test2.txt')
            try:
                remote = '/home/ubuntu/perf/%s.stat' % file_name
                scp.get(remote, '/home/ubuntu/perf')
            except Exception:
                print("Error!")
            finally:
                scp.close()

        #stdout = copy.communicate()[0]
        #print('STDOUT: %s' % stdout)
        events = {}
        with open('%s/perf/%s.stat' % (home, file_name)) as fp:
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()
            while line:
                sline = line.strip().split(";")
                event = sline[3]
                count = sline[1]
                if "not" in count:
                    count = 0
                if event not in events:
                    events[event] = []
                events[event].append(int(count))
                line = fp.readline()
        events_avg = {}
        for event in events:
            #avg = mean(events[event])
            events_avg[event] = [mean(events[event])]
        return DataFrame(events_avg,columns=list(events_avg.keys()))

