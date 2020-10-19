import keras
import time
import sys
import h5py
import kerastuner
import lib.rapl as rapl
import tensorflow as tf

from kerastuner.tuners import Hyperband

from scipy.stats import randint as sp_randint
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelBinarizer

from sklearn.base import BaseEstimator

from tensorflow.keras.models import Sequential, Model, load_model                                       
from tensorflow.keras.layers import Dense, Dropout, Flatten                                                    
from tensorflow.keras.layers import Conv1D, MaxPooling1D
from tensorflow.keras.layers import BatchNormalization                                           
from tensorflow.keras.layers import LeakyReLU

from tensorflow import keras


from sklearn.model_selection import train_test_split

start_energy = 0
end_energy = 0


class MyTuner(kerastuner.tuners.Hyperband):
    def run_trial(self, trial, *args, **kwargs):
        kwargs['batch_size'] = trial.hyperparameters.Choice('batch_size', values=[32, 64, 96, 128, 192, 256, 384, 512, 768, 1024])
        #print(trial.get_state())
        super(MyTuner, self).run_trial(trial, *args, **kwargs)
    def on_epoch_end(self, trial, model, epoch, logs):
        
        #start_time = trial.get_state()['metrics']['metrics']['start_time']['observations'][0]['value'][-1]
        start_time = trial.metrics.get_last_value('start_time')        

        error = logs['mean_absolute_percentage_error']
        #trial.metrics.update('error', error)
        print(logs)
        num_epochs = trial.get_state()['hyperparameters']['values']['tuner/epochs']
        error_resp = abs(100-error)/((time.time()-start_time)/(1))

        logs['error_resp'] = error_resp
        logs['error'] = error
        
        trial.metrics.update('error', error, step=epoch+1)
        trial.metrics.update('error_resp', error_resp, step=epoch+1)  

        #trial.metrics.update('error_resp', error_resp)
        print(trial.get_state()['metrics']['metrics']['start_time']['observations'])
        super(MyTuner, self).on_epoch_end(trial, model, epoch, logs)         

    def on_trial_begin(self, trial):
        global start_energy
        start_energy = rapl.RAPLMonitor.sample()
        if not trial.metrics.exists('error_resp'):
            trial.metrics.register('error_resp', direction='max')
        trial.metrics.update('start_time', time.time()-delay)
        #trial.metrics.update('energy', rapl.RAPLMonitor.sample().energy('package-0'))
        super(MyTuner, self).on_trial_begin(trial) 
    def on_trial_end(self, trial):
        global end_energy, start_energy
        end_energy = rapl.RAPLMonitor.sample()
        diff = end_energy-start_energy
        #start_energy = trial.metrics.get_last_value('energy')#trial.get_state()['metrics']['metrics']['energy']['observations'][0]['value'][-1]
        trial.metrics.update('energy', diff.energy('package-0'))#rapl.RAPLMonitor.sample().energy('package-0')-start_energy)
        trial.metrics.update('training_time', time.time()-trial.metrics.get_last_value('start_time'))
        super(MyTuner, self).on_trial_end(trial)

        
        global job, cores

        energy = trial.metrics.get_last_value('energy')#trial.get_state()['metrics']['metrics']['energy']['observations'][0]['value'][-1]
        error = trial.metrics.get_last_value('error')#trial.get_state()['metrics']['metrics']['error']['observations'][0]['value'][-1]
        error_resp = trial.metrics.get_last_value('error_resp')#trial.get_state()['metrics']['metrics']['error_resp']['observations'][0]['value'][-1]
        epochs = trial.get_state()['hyperparameters']['values']['tuner/epochs']
        batch = trial.get_state()['hyperparameters']['values']['batch_size']
        lr = trial.get_state()['hyperparameters']['values']['lr']
        training_time = time.time()-trial.metrics.get_last_value('start_time')#trial.get_state()['metrics']['metrics']['start_time']['observations'][0]['value'][-1]
        #error = 100-error_resp*training_time
        with open('offline_res/TuneV1Vary_'+job+'_'+str(cores)+'.csv', 'a') as f:
            f.write(str(lr)+','+str(epochs)+','+str(batch)+','+str(error)+','+str(error_resp)+','+str(training_time)+','+str(energy)+'\n')
        #super(MyTuner, self).on_trial_end(trial)
        print(trial.get_state())
        

def read_data(job):                                                                           
    with h5py.File('jobs/'+job+'_X.h5', 'r') as hf:                                                      
        data_X = hf[job+'_X'][:]                                                                 
    with h5py.File('jobs/'+job+'_Y.h5', 'r') as hf:                                                      
        data_Y = hf[job+'_Y'][:]                                                                 
                                                                                                
    train_X, test_X, train_Y, test_Y = train_test_split(data_X, data_Y, test_size=0.3, random_state=13)
                                                                                                
    return (train_X, train_Y), (test_X, test_Y)


def build_model(hp):
    global num_filters, num_dense, filters, hidden, drop                                                                        
    cnn_model = Sequential()                                                                    
                                                                                                
    cnn_model.add(Conv1D(filters, kernel_size=(8,),strides=2,activation='linear',input_shape=(40, 72),padding='same'))
    cnn_model.add(BatchNormalization())                                                         
    cnn_model.add(LeakyReLU(alpha=0.1))                                                         
    #cnn_model.add(MaxPooling1D((2,),padding='same'))                                            
    cnn_model.add(Dropout(drop))                                                      
                                                                                                
                                                                                                
    for i in range(0, num_filters-1):                                                 
        cnn_model.add(Conv1D(filters, kernel_size=(8,),strides=2,activation='linear',padding='same'))
        cnn_model.add(BatchNormalization())                                                     
        cnn_model.add(LeakyReLU(alpha=0.1))                                                     
        #cnn_model.add(MaxPooling1D((2,),padding='same'))                                            
        cnn_model.add(Dropout(drop))                                                  
    for i in range(0, num_filters):                                                   
        cnn_model.add(Conv1D(filters, (6,), strides=2,activation='linear',padding='same'))
        cnn_model.add(BatchNormalization())                                                     
        cnn_model.add(LeakyReLU(alpha=0.1))                                                     
        #cnn_model.add(MaxPooling1D(pool_size=(2,),padding='same'))                                  
        cnn_model.add(Dropout(drop))                                                  
    for i in range(0, num_filters):                                                   
        cnn_model.add(Conv1D(filters, (4,), activation='linear',padding='same'))      
        cnn_model.add(BatchNormalization())                                                     
        cnn_model.add(LeakyReLU(alpha=0.1))                                                     
        #cnn_model.add(MaxPooling1D(pool_size=(2,),padding='same'))                                  
        cnn_model.add(Dropout(drop))                                                  
    for i in range(0, num_filters):                                                   
        cnn_model.add(Conv1D(filters, (2,), strides=2,activation='linear',padding='same'))
        cnn_model.add(BatchNormalization())                                                     
        cnn_model.add(LeakyReLU(alpha=0.1))                                                     
        #cnn_model.add(MaxPooling1D(pool_size=(2,),padding='same'))                                  
        cnn_model.add(Dropout(drop))



    cnn_model.add(Flatten())                                                                    
    #cnn_model.add(BatchNormalization())                                                         
                                                                                                
    for i in range(0, num_dense):                                                     
        cnn_model.add(Dense(hidden))                                                  
        cnn_model.add(BatchNormalization())                                                     
        cnn_model.add(LeakyReLU(alpha=0.1))                                                     
        cnn_model.add(Dropout(drop))                                                  
                                                                                                
                                                                                                
    cnn_model.add(Dense(1))                                                                     
                                                                                                
                                                                                                
    cnn_model.compile(                                                                          
        loss=keras.losses.mean_squared_error,                                                   
        optimizer=keras.optimizers.Adam(lr=hp.Choice('lr', values = [0.1, 0.01, 0.001]), clipnorm=1. ),                         
        metrics=["mean_absolute_percentage_error"]                                              
    )                                                                                           
                                                                                            
    return cnn_model


#def error_resp(pred, true):
#    return abs(1-abs(pred-true)/true)


job = sys.argv[1]
delay = float(sys.argv[2])
cores = int(sys.argv[3])
load = float(sys.argv[4])

num_filters = int(sys.argv[5]) 
num_dense = int(sys.argv[6])
filters = int(sys.argv[7])
hidden = int(sys.argv[8])
drop = float(sys.argv[9])



tf.config.threading.set_inter_op_parallelism_threads(cores)                                             
tf.config.threading.set_intra_op_parallelism_threads(cores)

train, test = read_data(job)


tuner = MyTuner(
    build_model,
    objective='mean_absolute_percentage_error',#kerastuner.Objective("error_resp", direction="max"),
    factor=4,
    hyperband_iterations=2,
    executions_per_trial=1,
    max_epochs=50,
    directory='output',
    project_name='middleware-'+job
    )

s1 = rapl.RAPLMonitor.sample()
bf = time.time()

tuner.search(train[0], train[1], validation_data=(test[0], test[1]))#, callbacks=[tf.keras.callbacks.EarlyStopping(patience=50)])

af = time.time()
s2 = rapl.RAPLMonitor.sample()

diff = s2-s1
energy = diff.energy("package-0")
print("tuning energy:", energy)
print("tuning time:", af-(bf-delay))

tuner.results_summary()
print(tuner.oracle.get_best_trials(1)[0].get_state())

#with open('TuneV1Load_'+str(load)+'_'+str(cores)+'.csv', 'a') as f:
    #load,job,cores,lr,batch_size,epochs,queue_delay,tuning_time,response_time,tuning_energy,model_error,training_time,training_energy,obj_value
    #f.write(str(load)+','+job+','+str(cores)+','+str(tuner.oracle.get_best_trials(1)[0].get_state()['hyperparameters']['values']['lr'])+','+str(tuner.oracle.get_best_trials(1)[0].get_state()['hyperparameters']['values']['batch_size'])+','+str(tuner.oracle.get_best_trials(1)[0].get_state()['hyperparameters']['values']['tuner/epochs'])+','+str(delay)+','+str(af-bf)+','+str(af-(bf-delay))+','+str(energy)+','+str(tuner.oracle.get_best_trials(1)[0].metrics.get_last_value('error'))+','+str(tuner.oracle.get_best_trials(1)[0].metrics.get_last_value('training_time'))+','+str(tuner.oracle.get_best_trials(1)[0].metrics.get_last_value('energy'))+','+str(tuner.oracle.get_best_trials(1)[0].metrics.get_last_value('error_resp'))+'\n')
