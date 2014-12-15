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
import urllib.request
import os

Gst.init(None)

class FileTool(Thread):
    def __init__(self, path):
        super(FileTool, self).__init__()
        self.path = path
        self.samples = None

    def run(self):
        """Thread loop. Start with load_file() method.
        """
        path = self.path
        if os.name == 'nt':
            path = path.replace("\\", "\\\\")
        app_args = [
            'filesrc',
            'location="%s"'%(path),
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
        (res, state, pending) = pipeline.get_state(Gst.CLOCK_TIME_NONE)
        if res == Gst.StateChangeReturn.FAILURE:
            GLib.idle_add(self.ui_cb, self.row, Classifier.ERROR, "Gstreamer error (missing plugin?)")
            return
        self.samples = np.array([])
        
        # tell main thread we are loading
        GLib.idle_add(self.ui_cb, self.row, Classifier.LOADING, None)
        while True:
            sample = app.emit('pull-sample')
            if sample == None:
                break

            buf = sample.get_buffer()
            data = buf.extract_dup(0, buf.get_size())
            self.samples = np.append(self.samples, np.frombuffer(data, np.dtype('<i2')))

        GLib.idle_add(self.ui_cb, self.row, None, "Načteno")

    def load_file(self, sampling_rate, row, callback):
        """starts async thread which loads file
        :param sampling_rate: training vector
        :param row: actual row in table for callback
        :param callback: UI thread callback indicating actual state
        """
        if self.samples is not None:
            return
        self.ui_cb = callback
        self.row = row
        self.sampling_rate = sampling_rate
        self.start()

    def play(self):
        """plays file using Gstreamer
        """
        pipeline = Gst.parse_launch("playbin uri=file:{0}".format(urllib.request.pathname2url(self.path)))
        pipeline.set_state(Gst.State.PLAYING)
        
