import gi, numpy
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

Gst.init(None)

class File(GObject.GObject):
    def __init__(self, path):
        GObject.GObject.__init__(self)
        
        app_args = [
            'filesrc',
            'location="%s"'%(path),
            '!',
            'decodebin', '!',
            'audioconvert', '!',
            'audioresample', '!',
            'audio/x-raw,format=S16LE,channels=1,rate=8000', '!',
            'appsink',
                'name=app',
            ]
        
        play_args = [
            'filesrc',
            'location="%s"'%(path),
            '!',
            'decodebin',
            '!',
            'pulsesink'
            ]

        self.app_cmd = " ".join(app_args)
        self.play_cmd = " ".join(play_args)
        self.path = path

        # load file
        pipeline = Gst.parse_launch(self.app_cmd)
        app = pipeline.get_by_name('app')

        pipeline.set_state(Gst.State.PLAYING)
        self.samples = []
        while True:
            sample = app.emit('pull-sample')
            if sample == None:
                break
            buf = sample.get_buffer()
            data = buf.extract_dup(0, buf.get_size())
            self.samples += numpy.frombuffer(data, numpy.dtype('<i2')).tolist()

    def play_file(self):
        pipeline = Gst.parse_launch(self.play_cmd)
        pipeline.set_state(Gst.State.PLAYING)
        
