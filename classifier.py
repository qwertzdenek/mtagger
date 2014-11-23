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

    def __init__(self, sampling_rate, clfile, row, callback):
        self.clfile = clfile
        self.row = row
        self.ui_cb = callback
        self.sampling_rate = sampling_rate

    def classify(self):
        if not Classifier.learned:
            self.ui_cb(self.row, None, "N/A klasifikace")
            return

        self.feat = mfcc(self.clfile.samples, self.sampling_rate, VAD=simpleVAD)
        self.res = Classifier.clf.predict(self.feat)

        try:
            cls = int(mode(self.res))
        except statistics.StatisticsError as e:
            self.ui_cb(self.row, None, "!nerozhodnutené!")
            return
        self.ui_cb(self.row, Classifier.CLASSIFIED, cls)

    def new_training(X, y):
        Classifier.clf = svm.LinearSVC(C=0.9)
        try:
            Classifier.clf.fit_transform(X, y)
        except ValueError as e:
            return False;
        Classifier.learned = True
        return True

