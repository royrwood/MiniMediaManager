import sys

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject, Gdk, GLib

from mmm.file_scanner import FileScannerPanel
from mmm.file_browser import FileBrowserPanel
from mmm.constraint_poc import ConstraintLayoutDemo


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(default_width=1200, default_height=800, *args, **kwargs)

        self.file_scanner_panel = FileScannerPanel()
        self.file_scanner_panel.connect('file_added', self.file_added_handler)

        self.file_browser_panel = FileBrowserPanel()

        self.simple_grid = ConstraintLayoutDemo()

        self.notebook = Gtk.Notebook(margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        self.notebook.append_page(self.file_browser_panel, Gtk.Label(label='Files'))
        self.notebook.append_page(self.file_scanner_panel, Gtk.Label(label='Scanning'))
        self.notebook.append_page(self.simple_grid, Gtk.Label(label='ConstraintLayout'))
        self.set_child(self.notebook)

    def file_added_handler(self, _signal_factory, filename):
        print(f'MainWindow:file_added_handler: {filename}')


class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.win = None

    def do_activate(self):
        active_window = self.props.active_window
        if active_window:
            active_window.present()
        else:
            self.win = MainWindow(application=self)
            self.win.present()


if __name__ == '__main__':
    app = MyApp(application_id="com.example.gtk4.columnview", flags=Gio.ApplicationFlags.FLAGS_NONE)
    app.run(sys.argv)
