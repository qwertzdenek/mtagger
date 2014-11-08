from gi.repository import GLib
from features import mfcc
from threading import Thread

GLib.threads_init()

class Classifier():
    LOADING = 1
    CLASSIFYING = 2

    def run(self, clfile):
        clfile.load_file(self.notify_loading)
        # TODO: klasifikace
        mfcc_feat = mfcc(clfile.samples,16000)
        print(mfcc_feat)
        GLib.idle_add(self.ui_cb, self.row, None, 0, "Flétna")

    def notify_loading(self):
        self.progress += 1
        GLib.idle_add(self.ui_cb, self.row, Classifier.LOADING, self.progress, "Načítám")

    # run loading by this
    # row number
    # ui update method (should be called on UI thread)
    def do_classify(self, clfile, row, callback):
        self.row = row
        self.ui_cb = callback
        self.progress = 0
        Thread(target=self.run, args=(clfile,)).start()

