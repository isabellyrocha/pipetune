from pandas import DataFrame
from influxdb import InfluxDBClient
from sklearn.externals import joblib
from sklearn.cluster import KMeans

class GroundTruth():
    def __init__(self):
        #self.influx_client = InfluxDBClient(args.influx_host, args.influx_port, args.influx_user, args.influx_pass, args.influx_database)        
        self.influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'ground_truth')

    def model_init(self):
        events = {}
        config = []
        with open('/home/ubuntu/pipetune/utils/data/model.csv') as fp:
            line = fp.readline().strip()
            while line:
                (model, dataset, cores, 
                memory, batch, log_id,
                epoch, event, count, duration) = line.split(",")
                name = "%s,%s,%s,%s,%s,%s,%s" % (model, dataset, cores, memory, batch, epoch, duration)
                if int(epoch) > 0:
                    if event not in events:
                        events[event] = []
                    events[event].append(count)
                    if name not in config:
                        config.append(name)
                line = fp.readline()

        df = DataFrame(events,columns=list(events.keys()))
        model = KMeans(n_clusters=3)
        kmeans = model.fit(df)
        
        result = []
        for i in range(len(config)):
            result.append("%s,%d" % (config[i], kmeans.labels_[i]))

        self.save_clusters(result)
       
        joblib.dump(model, '/home/ubuntu/pipetune/utils/data/model.pkl')

    def save_clusters(self, result):
        clusters = {}
        for i in range(len(result)):
            (model, dataset, cores,
            memory, batch, epoch,
            duration, cluster) = result[i].split(",")
            if cluster not in clusters:
                clusters[cluster] = {
                    'cores': cores, 
                    'memory': memory,
                    'duration': duration.strip()
                }
            else:
                if int(duration) < int(clusters[cluster]['duration']):
                    clusters[cluster] = {
                        'cores': cores,
                        'memory': memory,
                        'duration': duration.strip()
                    }
        self.influx_client.query("drop measurement clusters")
        for cluster in clusters:
            ##c_config = best_config[i].split(",")
            #tags = {'cluster': i, 'cores': c_config[2], 'memory': c_config[3]}
            #duration = c_config[5]
            self.write_config(cluster, clusters[cluster])

    def write_config(self, cluster: str, fields: dict):
        json_body = [
        {
            "measurement": "clusters",
            "tags": { 
                "clusterID": cluster
            },
            "fields": fields
        }
        ]
#        self.influx_client.query("drop measurement clusters")
        self.influx_client.write_points(json_body)

    def getConfig(self, metrics):
        model = joblib.load('/home/ubuntu/pipetune/utils/data/model.pkl')
        score = model.score(metrics)
        print(score)
        print(model.inertia_)
        if score < -model.inertia_/2:
            return None
        prediction = model.predict(metrics)
        return self.get_config(prediction[0])

    def get_config(self, cluster):
        print("CLUSTER: %s" % cluster)
        result = self.influx_client.query('SELECT * '
                'FROM "clusters" '
                'WHERE clusterID =~ /%s/' % (cluster))
        cluster = list(result.get_points(measurement='clusters'))[0]
        cores = cluster['cores']
        memory = cluster['memory']
        return (cores, memory)
        #return list(result.get_points(measurement='ground_truth/config'))
''' 
    def get_config(self, measurements):
        model = joblib.load('data/model.pkl')   
        score = model.score(measurements)
        if score <= model.inertia_:
            prediction = model.predict(measurements)
            return self.get_config(prediction)
        return None
'''
