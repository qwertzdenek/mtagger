from gi.repository import GLib
#from features import mfcc
from threading import Thread

GLib.threads_init()

class Classifier(Thread):
    LOADING = 1
    CLASSIFYING = 2

    def __init__(self, clfile, row, callback):
        super(Classifier, self).__init__()
        self.clfile = clfile
        self.row = row
        self.ui_cb = callback
        self.progress = 0

    def run(self):
        self.clfile.load_file(self.notify_loading)
        # TODO: klasifikace
        #mfcc_feat = mfcc(clfile.samples,16000)
        #print(mfcc_feat)
        GLib.idle_add(self.ui_cb, self.row, None, 0, "Flétna")

    def notify_loading(self):
        self.progress += 1
        GLib.idle_add(self.ui_cb, self.row, Classifier.LOADING, self.progress, "Načítám")

