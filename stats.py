#!/usr/bin/python3

import gi, numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from features import mfcc
from VoiceActivityDetection import simpleVAD
from scipy import stats
from sklearn import svm
from sklearn import grid_search
import os
import random
import pickle

Gst.init(None)

def open_file(path, sampling_rate):
    app_args = [
        'filesrc',
        'location="%s"'%(path),
        '!',
        'decodebin', '!',
        'audioconvert', '!',
        'audioresample', '!',
        'audio/x-raw,format=S16LE,channels=1,rate=%d'%(sampling_rate), '!',
        'appsink',
        'name=app',
        'sync=false' ]

    pipeline = Gst.parse_launch(" ".join(app_args))
    app = pipeline.get_by_name('app')

    pipeline.set_state(Gst.State.PLAYING)
    samples = np.array([])

    while True:
        sample = app.emit('pull-sample')
        if sample == None:
            break

        buf = sample.get_buffer()
        data = buf.extract_dup(0, buf.get_size())
        samples = np.append(samples, np.frombuffer(data, np.dtype('<i2')))
    return samples

# main
os.chdir('sounds')
instruments = os.listdir()

X = []
y = []

take=20
clsid=0
for inst in instruments:
    names = os.listdir(path=inst)
    names = random.sample(names, take)
    for f in names:
        samples = open_file(os.path.join(os.getcwd(), inst, f), 16000)
        feat = mfcc(samples,16000, appendEnergy=False, winlen=0.030, VAD=simpleVAD)
        # add two symptoms from the middle
        X.append(feat[len(feat) / 2 + 5])
        y.append(clsid)
        X.append(feat[len(feat) / 2 - 3])
        y.append(clsid)
        X.append(feat[len(feat) / 2 - 5])
        y.append(clsid)
    clsid += 1
    
#clf = svm.SVC()

#param_grid = {'C': [0.5, 5, 50, 500], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}

#gse = grid_search.GridSearchCV(clf, param_grid, n_jobs=os.cpu_count())
#gse.fit(X, y)

os.chdir('..')
with open('dataset.pickle', 'wb') as f:
    pickle.dump((X, y, dict(zip(range(0, len(instruments)), instruments))), f, pickle.HIGHEST_PROTOCOL)

quit()

clsid=0
cfile=0
error=0
for inst in instruments:
    names = os.listdir(path=inst)
    cfile += len(names)
    for f in names:
        samples = open_file(os.path.join(os.getcwd(), inst, f), 16000)
        feat = mfcc(samples,16000, appendEnergy=False, winlen=0.030, VAD=simpleVAD)
        res = gse.predict(feat[range(int(len(feat) / 2 - 10), int(len(feat) / 2 + 2))])
        cls = int(stats.mode(res)[0])
        if cls != clsid:
            error += 1
    clsid += 1

mse = error / cfile
print("MSE was {0} ({1} test files)".format(mse, cfile))

#print('data=[')
#for coef in X:
#    for j in coef.tolist():
#        print('%f '%(j), end="")
#    print(';')
#print(']')
#print('y=', end="")
#print(y)

