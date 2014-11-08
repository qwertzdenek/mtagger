from gi.repository import Gtk
from file_tool import FileTool
from classifier import Classifier

M_NAME = 0  # filename
M_CLASS = 1 # classname
M_PRG = 2   # progress value
M_PRGM = 3  # progress message
M_PRGV = 4  # progress visibility

class MainWindow:
    def __init__(self, target):
        self.target = target
    
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(self)
        
        self.window = self.builder.get_object("window")
        self.file_dialog = self.builder.get_object("file_dialog")
        self.file_store = self.builder.get_object("filestore")
        self.file_view = self.builder.get_object("fileview")

        self.last_dir = None
        
        # all_files list of File tuples
        self.all_files = []
        # sel_files: indexes to the all_files tuple
        self.sel_files = []
        
        self.window.show_all()

    def open_button_clicked_cb(self, button):
        if self.last_dir is not None:
            self.file_dialog.set_current_folder_uri(self.last_dir)

        response = self.file_dialog.run()

        if response == 1:
            self.last_dir = self.file_dialog.get_current_folder_uri()
            for f in self.file_dialog.get_filenames():
                iter = self.file_store.append([f, "N/A", 0, None, False])
                self.all_files.append(FileTool(f))

        self.file_dialog.hide()

    def del_button_clicked_cb(self, button):
        if not len(self.sel_files):
            return
        row = self.sel_files[0]
        del_iter = self.file_store.get_iter(self.file_view.get_path_at_pos(0, row)[0])
        self.file_store.remove(del_iter)
        del self.all_files[row]

    def play_button_clicked_cb(self, button):
        if not len(self.sel_files):
            return
        self.all_files[self.sel_files[0]].play()
        
    def cl_button_clicked_cb(self, button):
        if not len(self.sel_files):
            return
        row = self.sel_files[0]
        self.target.do_classify(self.all_files[row], row, self.update_classify_progress_cb)

        #for f in self.sel_files[1]:
        #    cls = self.target.do_classify(f[0])
        #    self.file_store[self.sel_files[0].get_iter(f[1])][1] = cls

    def fileview_selection_changed_cb(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        self.sel_files = []
        for path in pathlist:
            self.sel_files += path.get_indices()

    def update_classify_progress_cb(self, row, state, progress, message):
        new_iter = self.file_store.get_iter(self.file_view.get_path_at_pos(0, row)[0])
        if state == Classifier.LOADING:
            self.file_store[new_iter][M_CLASS] = "N/A"
            self.file_store[new_iter][M_PRG] = progress
            self.file_store[new_iter][M_PRGM] = message
            self.file_store[new_iter][M_PRGV] = True
        elif state == Classifier.CLASSIFYING:
            print("Klasifikace")
            # probíhá klasifikace
        elif state is None:
            self.file_store[new_iter][M_CLASS] = message
            self.file_store[new_iter][M_PRGV] = False
    def destroy(self, window):
        Gtk.main_quit()

    def main(self):
        Gtk.main()
