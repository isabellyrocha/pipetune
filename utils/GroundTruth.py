from pandas import DataFrame
from influxdb import InfluxDBClient
from sklearn.externals import joblib
from sklearn.cluster import KMeans
from pathlib import Path

HOME = str(Path.home())

class GroundTruth():
    def __init__(self):
        self.influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'ground_truth')

    def model_init(self):
        events = {}
        config = []
        with open('%s/pipetune/clustering/model.csv' % HOME) as fp:
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
       
        joblib.dump(model, '%s/pipetune/clustering/model.pkl' % HOME)

    def save_clusters(self, result):
        clusters = {}
        for i in range(len(result)):
            (model, dataset, cores,
            memory, batch, epoch,
            duration, cluster) = result[i].split(",")
            tags = (cluster, batch)
            if tags not in clusters:
                clusters[tags] = {
                    'cores': cores, 
                    'memory': memory,
                    'duration': duration.strip()
                }
            else:
                if int(duration) < int(clusters[tags]['duration']):
                    clusters[tags] = {
                        'cores': cores,
                        'memory': memory,
                        'duration': duration.strip()
                    }
        for tags_cluster in clusters:
            self.write_config(tags_cluster, clusters[tags_cluster])

    def write_config(self, tags, fields):
        json_body = [
        {
            "measurement": "clusters",
            "tags": { 
                "clusterID": tags[0],
                "batch": tags[1]
            },
            "fields": fields
        }
        ]
        self.influx_client.query("drop measurement clusters")
        self.influx_client.write_points(json_body)

    def getConfig(self, metrics, batch):
        model = joblib.load('%s/pipetune/clustering/model.pkl' % HOME)
#        score = model.score(metrics)
        score = 0
        if True:#score < -model.inertia_/2:
            return None
        prediction = model.predict(metrics)
        return self.get_config(prediction[0], batch)

    def get_config(self, cluster, batch):
        result = self.influx_client.query('SELECT * '
                'FROM "clusters" '
                'WHERE clusterID =~ /%s/ and batch =~ /%s/' % (cluster, batch))
        cluster = list(result.get_points(measurement='clusters'))[0]
        cores = cluster['cores']
        memory = cluster['memory']
        return (cores, memory)
