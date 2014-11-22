import pickle
import numpy as np
from gi.repository import Gtk
from file_tool import FileTool
from classifier import Classifier
from features import mfcc
from VoiceActivityDetection import simpleVAD

class MainWindow:
    SR = 16000

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(self)
        
        self.window = self.builder.get_object("window")
        self.file_store = self.builder.get_object("filestore")
        self.file_view = self.builder.get_object("fileview")
        self.status_label = self.builder.get_object("status")
        self.run_indicator = self.builder.get_object("running")
        self.audiofilter = self.builder.get_object("audiofilter")
        self.classcombo = self.builder.get_object("classcombo")
        
        self.file_dialog = Gtk.FileChooserDialog("Otevřít", self.window, Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.file_dialog.add_filter(self.audiofilter)
        self.file_dialog.set_select_multiple(True)

        self.last_dir = None

        # all_files tuple of Files
        self.all_files = []
        # sel_files: indexes to the all_files tuple
        self.sel_files = []
        
        self.X = []
        self.y = []
        self.class_names = {}
        
        try:
            with open('dataset.pickle', 'rb') as f:
                (self.X, self.y, self.class_names) = pickle.load(f)
                for name in self.class_names.items():
                    self.classcombo.append(str(name[0]), name[1])
                ok = Classifier.new_training(self.X, self.y)
                if ok:
                    self.status_label.set_text("{0} vzorků, {1} tříd".format(len(self.X), len(self.class_names)))
        except IOError as e:
            pass

        self.window.show_all()

    def open_button_clicked_cb(self, button):
        if self.last_dir is not None:
            self.file_dialog.set_current_folder_uri(self.last_dir)

        response = self.file_dialog.run()

        if response == Gtk.ResponseType.OK:
            self.last_dir = self.file_dialog.get_current_folder_uri()
            file_names = self.file_dialog.get_filenames()
            self.file_dialog.hide()
        else:
            self.file_dialog.hide()
            return

        self.run_indicator.start()
        self.window.set_sensitive(False)
        self.counter = len(file_names)
        for f in file_names:
            row = self.file_store.iter_n_children(None)
            self.file_store.append([f, "N/A"])
            fobj = FileTool(f);
            fobj.load_file(MainWindow.SR, row, self.update_classify_progress_cb)
            self.all_files.append(fobj)

    def del_button_clicked_cb(self, button):
        if not len(self.sel_files):
            return
        for i in range(len(self.sel_files)):
            row = self.sel_files[0]
            del_iter = self.file_store.get_iter(Gtk.TreePath.new_from_indices([row]))
            self.file_store.remove(del_iter)
            del self.all_files[row]

    def play_button_clicked_cb(self, button):
        if not len(self.sel_files):
            return
        self.all_files[self.sel_files[0]].play()

    def cl_button_clicked_cb(self, button):
        if not len(self.sel_files):
            return
        self.counter = -1
        for row in self.sel_files:
            cl = Classifier(MainWindow.SR, self.all_files[row], row, self.update_classify_progress_cb)
            cl.classify()

    def fileview_selection_changed_cb(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        self.sel_files = []
        for path in pathlist:
            self.sel_files += path.get_indices()

    # učí
    def classcombo_changed_cb(self, entry):
        class_id = entry.get_active()
        if class_id == -1:
            return
        self.fill(class_id)

    # vytvoří třídu
    def classcombo_entry_activated_cb(self, entry):
        class_desc = entry.get_text()
        if class_desc in self.class_names.values():
            return
        class_id = len(self.class_names)
        self.class_names[len(self.class_names)] = class_desc
        self.classcombo.remove_all()
        for name in self.class_names.items():
            self.classcombo.append(str(name[0]), name[1])

        self.fill(class_id)

    def fill(self, class_id):
        # get training samples
        for i in range(len(self.sel_files)):
            row = self.sel_files[0]
            samples = self.all_files[row].samples
            feat = mfcc(samples,16000, VAD=simpleVAD)
            # add two symptoms from the middle
            self.X.append(feat[len(feat) / 2 - 1])
            self.y.append(class_id)
            self.X.append(feat[len(feat) / 2 + 1])
            self.y.append(class_id)
            
            # clear from the list
            del_iter = self.file_store.get_iter(Gtk.TreePath.new_from_indices([row]))
            self.file_store.remove(del_iter)
            del self.all_files[row]

        # print results
        if Classifier.new_training(self.X, self.y):
            self.status_label.set_text("{0} vzorků, {1} tříd".format(len(self.X), len(self.class_names)))
        else:
            self.status_label.set_text("Klasifikátor potřebuje víc tříd")

    def update_classify_progress_cb(self, row, state, message):
        new_iter = self.file_store.get_iter(Gtk.TreePath.new_from_indices([row]))
        if state == Classifier.LOADING:
            self.file_store[new_iter][1] = "Načítám"
        elif state == Classifier.CLASSIFIED:
            self.file_store[new_iter][1] = self.class_names[message]
        elif state is None:
            self.file_store[new_iter][1] = message
            self.counter -= 1
            if self.counter == 0:
                self.run_indicator.stop()
                self.window.set_sensitive(True)

    def destroy(self, window):
        with open('dataset.pickle', 'wb') as f:
            pickle.dump((self.X, self.y, self.class_names), f, pickle.HIGHEST_PROTOCOL)
        Gtk.main_quit()

    def main(self):
        Gtk.main()
