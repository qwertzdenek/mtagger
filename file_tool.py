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

import gi, numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst
from threading import Thread
from classifier import Classifier

GLib.threads_init()
Gst.init(None)

class FileTool(Thread):
    def __init__(self, path):
        super(FileTool, self).__init__()
        self.path = path
        self.samples = None

    def run(self):
        app_args = [
            'filesrc',
            'location="%s"'%(self.path),
            '!',
            'decodebin', '!',
            'audioconvert', '!',
            'audioresample', '!',
            'audio/x-raw,format=S16LE,channels=1,rate=%d'%(self.sampling_rate), '!',
            'appsink',
                'name=app',
                'sync=false' ]

        pipeline = Gst.parse_launch(" ".join(app_args))
        app = pipeline.get_by_name('app')

        pipeline.set_state(Gst.State.PLAYING)
        self.samples = np.array([])
        cntr = 0
        while True:
            cntr += 1
            sample = app.emit('pull-sample')
            if sample == None:
                break
            
            if cntr == 10:
                GLib.idle_add(self.ui_cb, self.row, Classifier.LOADING, None)
                cntr = 0

            buf = sample.get_buffer()
            data = buf.extract_dup(0, buf.get_size())
            self.samples = np.append(self.samples, np.frombuffer(data, np.dtype('<i2')))

        GLib.idle_add(self.ui_cb, self.row, None, "Načteno")

    def load_file(self, sampling_rate, row, callback):
        if self.samples is not None:
            return
        self.ui_cb = callback
        self.row = row
        self.sampling_rate = sampling_rate
        self.start()

    def play(self):
        play_args = [
            'filesrc',
            'location="%s"'%(self.path),
            '!',
            'decodebin',
            '!',
            'pulsesink'
            ]

        pipeline = Gst.parse_launch(" ".join(play_args))
        pipeline.set_state(Gst.State.PLAYING)
        
