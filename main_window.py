from gi.repository import Gtk

class MainWindow:
    def __init__(self, target):
        self.target = target
    
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(self)
        
        self.window = self.builder.get_object("window")
        self.file_dialog = self.builder.get_object("file_dialog")
        self.file_store = self.builder.get_object("filestore")
        
        self.last_dir = None
        self.path_list = []
        
        # tuple (TreeModel, [[filename, treepath], ...])
        self.sel_files = []
        
        self.window.show_all()

    def open_button_clicked_cb(self, button):
        if self.last_dir != None:
            self.file_dialog.set_current_folder_uri(self.last_dir)
        
        response = self.file_dialog.run()
        
        if response == 1:
            self.last_dir = self.file_dialog.get_current_folder_uri()
            for f in self.file_dialog.get_filenames():
                self.file_store.append([f, "N/A"])
        elif response == 0:
            print("response 0")

        self.file_dialog.hide()

    def del_button_clicked_cb(self, button):
        print("del_button_clicked_cb")
    def play_button_clicked_cb(self, button):
        print("play_button_clicked_cb")
    def cl_button_clicked_cb(self, button):
        for f in self.sel_files[1]:
            cls = self.target.do_classify(f[0])
            self.file_store[self.sel_files[0].get_iter(f[1])][1] = cls

    def fileview_selection_changed_cb(self, tree_selection):
        del self.sel_files # clear tuple
        (model, pathlist) = tree_selection.get_selected_rows()
        self.sel_files = (model, [])
        for path in pathlist:
            name = self.file_store[model.get_iter(path)][0];
            self.sel_files[1].append([name, path])

    def destroy(self, window):
        Gtk.main_quit()

    def main(self):
        Gtk.main()
