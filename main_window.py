from gi.repository import Gtk
import wave

class MainWindow:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("app.glade")
        self.builder.connect_signals(self)
        
        self.window = self.builder.get_object("window")
        self.window.show_all()

    def open_button_clicked_cb(self, button):
        dialog = Gtk.FileChooserDialog("Zvolte soubor", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        
        response = dialog.run()
        #if response == Gtk.ResponseType.OK:
        #    self.snd = wave.open(dialog.get_filename(), 'rb')
        #    print(self.snd);

        dialog.destroy()

    def del_button_clicked_cb(self, button):
        print("del_button_clicked_cb")
    def play_button_clicked_cb(self, button):
        print("play_button_clicked_cb")
    def cl_button_clicked_cb(self, button):
        print("cl_button_clicked_cb")

    def destroy(self, window):
        Gtk.main_quit()

    def main(self):
        Gtk.main()

