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
        Classifier.clf = svm.LinearSVC()
        try:
            Classifier.clf.fit(X, y)
        except ValueError as e:
            return False;
        Classifier.learned = True
        return True

