#!/usr/bin/python3

import numpy as np
from features import mfcc
from VoiceActivityDetection import simpleVAD
from scipy import stats
from sklearn import svm
from sklearn import grid_search
import os
import random
import pickle
import scipy.io.wavfile

# main
os.chdir('sounds/wav')
instruments = os.listdir()

X = []
y = []

set_size = 0
for take in range(5,15):
    clsid=0
    for inst in instruments:
        names = os.listdir(path=inst)
        names = random.sample(names, take)
        for f in names:
            samples = scipy.io.wavfile.read(os.path.join(os.getcwd(), inst, f))[1]
            feat = mfcc(samples,16000, appendEnergy=False, winlen=0.030, VAD=simpleVAD)
            # add two symptoms from the middle
            X.append(feat[int(random.random() * len(feat))])
            y.append(clsid)
            X.append(feat[int(random.random() * len(feat))])
            y.append(clsid)
            X.append(feat[int(random.random() * len(feat))])
            y.append(clsid)
            set_size += 3
        clsid += 1

    clf = svm.LinearSVC()

    param_grid = {'C': [0.5, 5, 50, 500], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}

    gse = grid_search.GridSearchCV(clf, param_grid, n_jobs=os.cpu_count())
    gse.fit(X, y)

    clsid=0
    cfile=0
    error=0
    for inst in instruments:
        names = os.listdir(path=inst)
        cfile += len(names)
        for f in names:
            samples = scipy.io.wavfile.read(os.path.join(os.getcwd(), inst, f))[1]
            feat = mfcc(samples,16000, appendEnergy=False, winlen=0.030, VAD=simpleVAD)
            res = gse.predict(feat[range(int(len(feat) / 2 - 15), int(len(feat) / 2 + 2))])
            cls = int(stats.mode(res)[0])
            if cls != clsid:
                error += 1
        clsid += 1

    mse = (error / cfile) * 100
    print("{0};{1}".format(set_size, mse))

os.chdir('../..')

ids=range(0,len(instruments))
sinst=dict(zip(ids, instruments))

print(sinst)

with open('dataset.pickle', 'wb') as f:
    pickle.dump((X, y, sinst), f, pickle.HIGHEST_PROTOCOL)

#print('data=[')
#for coef in X:
#    for j in coef.tolist():
#        print('%f '%(j), end="")
#    print(';')
#print(']')
#print('y=', end="")
#print(y)

