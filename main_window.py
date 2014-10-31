from gi.repository import Gtk

class MainWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(self)
        
        self.window = self.builder.get_object("window")
        self.file_dialog = self.builder.get_object("file_dialog")
        self.file_store = self.builder.get_object("filestore")
        
        self.window.show_all()

    def open_button_clicked_cb(self, button):
		# TODO: set directory from the self.last_dir
        response = self.file_dialog.run()
        
        if response == 1:
            self.last_dir = self.file_dialog.get_path()
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
        print("cl_button_clicked_cb")
        # TODO: send signal to the classificator

    def destroy(self, window):
        Gtk.main_quit()

    def main(self):
        Gtk.main()
