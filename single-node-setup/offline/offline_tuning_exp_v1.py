import os





cores = [1, 2, 4, 8]
jobs = ['spkmeans', 'bfs', 'jacobi']
#num_filters, num_dense, filters, hidden, drop
model = {
    'jacobi': [3, 3, 64, 128, 0.5],
    'spkmeans': [4, 5, 64, 128, 0.1],
    'bfs': [5, 5, 128, 256, 0.3]    
}
os.system('rm -rf output')
for j in jobs:
    for c in cores:
        config = model[j]
        os.system('python3.6 easy_offline_v1.py '+j+' 0 '+str(c)+' 0 '+' '.join([str(elem) for elem in config]))

        os.system('rm -rf output')
