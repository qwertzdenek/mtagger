import gi, numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

Gst.init(None)

class FileTool(GObject.GObject):
    def __init__(self, path):
        GObject.GObject.__init__(self)
        self.path = path

    def load_file(self, callback):
        # TODO: if self.samples exists do nothing
        app_args = [
            'filesrc',
            'location="%s"'%(self.path),
            '!',
            'decodebin', '!',
            'audioconvert', '!',
            'audioresample', '!',
            'audio/x-raw,format=S16LE,channels=1,rate=16000', '!',
            'appsink',
                'name=app',
            ]

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
                callback()
                cntr = 0
            buf = sample.get_buffer()
            data = buf.extract_dup(0, buf.get_size())
            self.samples = np.append(self.samples, np.frombuffer(data, np.dtype('<i2')))

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
        
