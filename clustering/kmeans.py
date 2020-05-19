from pandas import DataFrame
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
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

#for event in events:
#    print(len(events[event]))

#print(len(names))
#print(events)
#print(len(events.keys()))
  
df = DataFrame(events,columns=list(events.keys()))
  
#print(df)

km = KMeans(n_clusters=4)

kmeans = km.fit(df)

#print(kmeans.cluster_centers_)
#print(kmeans.labels_)

#print(kmeans.labels_)
#print(names)

for i in range(len(config)):
    print("%s,%d" % (config[i], kmeans.labels_[i]))


'''
results = {}
for i in range(len(config)):
    if kmeans.labels_[i] not in results:
        results[kmeans.labels_[i]] = {}
    sconfig = config[i].split(",")
    duration = int(sconfig[5])
    if duration not in results[kmeans.labels_[i]]:
        results[kmeans.labels_[i]][duration] = config[i]
    #print("%s,%s" % (config[i],kmeans.labels_[i]))
    #if kmeans.labels_[i] == 0:
    #     print("%s,%s" % (config[i],kmeans.labels_[i]))


for result in results:
    key = min(list(results[result].keys()))
    print(key)
    print("%s: %s" % (result, results[result][key]))


        


pca = PCA(3) 
pca.fit(df) 
  
pca_data = pd.DataFrame(pca.transform(df)) 
  
print(pca_data.head())

colors = list(zip(*sorted(( 
                    tuple(mcolors.rgb_to_hsv( 
                          mcolors.to_rgba(color)[:3])), name) 
                     for name, color in dict( 
                            mcolors.BASE_COLORS, **mcolors.CSS4_COLORS 
                                                      ).items())))[1] 
   
   
# number of steps to taken generate n(clusters) colors  
skips = math.floor(len(colors[1 : -1])/clusters) 
cluster_colors = colors[1 : -1 : skips] 

# generating correlation heatmap 
sns.heatmap(df.corr(), annot = False) 
  
# posting correlation heatmap to output console  
plt.show()
'''
