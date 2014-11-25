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
from statistics import mode
from VoiceActivityDetection import simpleVAD
from features import mfcc
from sklearn import svm

class Classifier():
    LOADING = 1
    CLASSIFIED = 2

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
        if not Classifier.learned:
            callback(row, None, "N/A klasifikace")
            return

        feat = mfcc(clfile.samples, sampling_rate, VAD=simpleVAD)
        res = Classifier.clf.predict(feat)

        try:
            cls = int(mode(res))
        except statistics.StatisticsError as e:
            callback(row, None, "!nerozhodnutené!")
            return
        callback(row, Classifier.CLASSIFIED, cls)

    def new_training(X, y):
        Classifier.clf = svm.LinearSVC(C=0.9)
        try:
            Classifier.clf.fit_transform(X, y)
        except ValueError as e:
            return False;
        Classifier.learned = True
        return True

