import os
import time

budget = 20
interval = 60
min_freq = '2.0GHz'
max_freq = '4.0GHz'

def set_frequency(freq):
    os.system('sudo cpupower frequency-set -u ' + freq + ' -d ' + freq)

while True:
    set_frequency(max_freq)
    time.sleep(budget)
    set_frequency(min_freq)
    time.sleep(interval-budget)
