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

import pickle
import os
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
        self.aboutdialog = self.builder.get_object("aboutdialog")

        self.file_dialog = Gtk.FileChooserDialog("Otevřít", self.window, Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.file_dialog.set_select_multiple(True)

        if os.name != 'nt':
            self.file_dialog.add_filter(self.audiofilter)
            self.audiofilter.set_name("Zvuk")

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
        """Open button callback
        :param button: signal came from this button
        """
        if self.last_dir is not None:
            self.file_dialog.set_current_folder_uri(self.last_dir)

        response = self.file_dialog.run()
        
        self.file_dialog.hide()
        
        if response == Gtk.ResponseType.OK:
            self.last_dir = self.file_dialog.get_current_folder_uri()
            file_names = self.file_dialog.get_filenames()
        else:
            return

        self.run_indicator.start()
        self.window.set_sensitive(False)
        self.counter = len(file_names)
        for f in file_names: # update file_store
            row = self.file_store.iter_n_children(None)
            self.file_store.append([os.path.basename(f), "N/A"])
            fobj = FileTool(f);
            fobj.load_file(MainWindow.SR, row, self.update_classify_progress_cb)
            self.all_files.append(fobj)

    def del_button_clicked_cb(self, button):
        """Delete button callback
        :param button: signal came from this button
        """
        if not len(self.sel_files):
            return
        # delete first item, this list will be updated imediatelly
        for i in range(len(self.sel_files)):
            row = self.sel_files[0]
            del_iter = self.file_store.get_iter(Gtk.TreePath.new_from_indices([row]))
            self.file_store.remove(del_iter)
            del self.all_files[row]

    def play_button_clicked_cb(self, button):
        """Play button callback
        :param button: signal came from this button
        """
        if not len(self.sel_files):
            return
        self.all_files[self.sel_files[0]].play()

    def cl_button_clicked_cb(self, button):
        """Classify button callback
        :param button: signal came from this button
        """
        if not len(self.sel_files):
            return
        self.counter = -1
        for row in self.sel_files:
            Classifier.classify(self.all_files[row], MainWindow.SR, row, self.update_classify_progress_cb)

    def about_button_clicked_cb(self, button):
        """Classify button callback
        :param button: signal came from this button
        """
        self.aboutdialog.run()
        self.aboutdialog.hide()

    def fileview_selection_changed_cb(self, tree_selection):
        """Table selection callback
        :param tree_selection: signal came from this button
        """
        (model, pathlist) = tree_selection.get_selected_rows()
        self.sel_files = []
        for path in pathlist:
            self.sel_files += path.get_indices()

    # učí
    def classcombo_changed_cb(self, entry):
        """Combobox list callback
        :param entry: signal came from this button
        """
        class_id = entry.get_active()
        if class_id == -1:
            return
        self.fill(class_id)
        self.classcombo.get_child().set_text("")

    # vytvoří třídu
    def classcombo_entry_activated_cb(self, entry):
        """Combobox entry update callback
        :param entry: signal came from this button
        """
        class_desc = entry.get_text()
        # add only new classes
        if class_desc in self.class_names.values():
            return
        class_id = len(self.class_names)
        self.class_names[len(self.class_names)] = class_desc
        self.classcombo.remove_all()
        for name in self.class_names.items():
            self.classcombo.append(str(name[0]), name[1])

        self.fill(class_id)

    def fill(self, class_id):
        """Fills internal structer with new training samples.
           Do not call directly.
        :param class_id: class identification
        """
        # get training samples
        for i in range(len(self.sel_files)):
            row = self.sel_files[0]
            samples = self.all_files[row].samples
            feat = mfcc(samples, 16000, winlen=0.030, VAD=simpleVAD)
            # add two symptoms from the middle
            self.X.append(feat[int(len(feat) / 2 - 1)])
            self.y.append(class_id)
            self.X.append(feat[int(len(feat) / 2 + 1)])
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
        """Callback function for classifier, file loader or any other caller.
           Must be done by UI thread
        :param row: actual updated row
        :param state: indicated state of caller
        :param message: message from caller
        """
        new_iter = self.file_store.get_iter(Gtk.TreePath.new_from_indices([row]))
        if state == Classifier.LOADING:
            self.file_store[new_iter][1] = "Načítám"
        elif state == Classifier.CLASSIFIED:
            self.file_store[new_iter][1] = self.class_names[message]
        elif state == Classifier.ERROR:
            self.status_label.set_text("ERROR: " + message)
            self.run_indicator.stop()
            self.window.set_sensitive(True)
        elif state is None:
            self.file_store[new_iter][1] = message
            self.counter -= 1
            if self.counter == 0:
                self.run_indicator.stop()
                self.window.set_sensitive(True)

    def destroy(self, window):
        """GTK callback when is window closed. Time to save application state.
        :param window: actual closed window
        """
        with open('dataset.pickle', 'wb') as f:
            pickle.dump((self.X, self.y, self.class_names), f, pickle.HIGHEST_PROTOCOL)
        Gtk.main_quit()

    def main(self):
        Gtk.main()
