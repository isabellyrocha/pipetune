from pandas import DataFrame
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.externals import joblib
from sklearn.decomposition import PCA 
from matplotlib import colors as mcolors 
import math 
import pandas as pd 
import seaborn as sns 

clusters = 4
events = {}
config = []

with open('../experiments/agg_per_event.log') as fp:
    line = fp.readline()
    while line:
        sline = line.split(",")
        model = sline[0]
        dataset = sline[1]
        cores = sline[2]
        memory = sline[3]
        batch = sline[4]
        #log_id = sline[5]
        event = sline[5]
        count = float(sline[6])
        duration = float(sline[7].strip())
        name = "%s,%s,%s,%s,%s,%d" % (model, dataset, cores, memory, batch, duration)
        if event not in events:
            events[event] = []
        #if int(phase) < 5 and int(phase) > 0:
        events[event].append(count)
        if name not in config:
            config.append(name)
        line = fp.readline()

df = DataFrame(events,columns=list(events.keys()))
model = KMeans(n_clusters=clusters)
print(model)
kmeans = model.fit(df)

joblib.dump(model, 'model.pkl')  
model_loaded = joblib.load('model.pkl')

print(model_loaded)


for i in range(len(config)):
    print("%s,%d" % (config[i], kmeans.labels_[i]))

# get test
test = {}
for event in list(events.keys()):
    test[event] = [events[event][0]]
print(test)
df_test = DataFrame(test,columns=list(test.keys()))


prediction = model.predict(df_test)
print(prediction)
