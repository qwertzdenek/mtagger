# coding=utf-8
"""
Copyright (c) 2014 Zdeněk Janeček

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

import numpy as np
from scipy import stats
from VoiceActivityDetection import simpleVAD
from features import mfcc
from sklearn import svm
from sklearn import grid_search
import os

class Classifier():
    LOADING = 1
    CLASSIFIED = 2
    ERROR = 3

    # indicates learned state
    learned = False
    clf = None

    def classify(clfile, sampling_rate, row, callback):
        """classifies connected file
        :param clfile: instance of file
        :param sampling_rate: sampling rate
        :param row: actual row in table
        :param callback: ui callback where classifier sends results
        :returns: nothing, but calls callback with results
        """
        if not Classifier.learned or clfile.samples is None:
            callback(row, Classifier.ERROR, "N/A klasifikace")
            return

        feat = mfcc(clfile.samples, sampling_rate, winlen=0.030, appendEnergy=False, VAD=simpleVAD)
        res = Classifier.clf.predict(feat[range(int(len(feat) / 2 - 4), int(len(feat) / 2 + 4))])

        cls = int(stats.mode(res)[0])
        callback(row, Classifier.CLASSIFIED, cls)

    def new_training(X, y):
        """reads training vector and fits new hypothesis
        :param X: training vector
        :param y: target vector (classes)
        :returns: True on success and False afterwards
        """
        clf = svm.SVC()
        param_grid = {'C': [0.5, 5, 50, 500], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}
        Classifier.clf = grid_search.GridSearchCV(clf, param_grid, n_jobs=os.cpu_count())
        try:
            Classifier.clf.fit(X, y)
        except ValueError as e:
            return False;
        Classifier.learned = True
        return True

