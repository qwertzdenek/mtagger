from gi.repository import GObject

class Classifier(GObject.GObject):
    def __init__(self):
        GObject.GObject.__init__(self)

    def do_classify(self, arg):
        print("classify {0}".format(arg))
        
        return "Něco"

