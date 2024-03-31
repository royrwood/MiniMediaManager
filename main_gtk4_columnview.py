import sys
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject, Gdk, GLib


class MyListModelDataItem(GObject.Object):
    __gtype_name__ = "MyListModelDataItem"

    def __init__(self, user_id, user_name_first, user_name_last):
        super().__init__()

        self._user_id = user_id
        self._user_name_first = user_name_first
        self._user_name_last = user_name_last

    @GObject.Property(type=str)
    def user_id(self):
        return self._user_id

    @GObject.Property(type=str)
    def user_name_first(self):
        return self._user_name_first

    @GObject.Property(type=str)
    def user_name_last(self):
        return self._user_name_last

    def __repr__(self):
        return f"MyListModelDataItem(id={self._user_id}, user_name={self._user_name_first} {self._user_name_last})"


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 600)

        self.list_store_model = Gio.ListStore(item_type=MyListModelDataItem)
        self.list_store_model.append(MyListModelDataItem(1, 'Karl', 'Barkley'))
        self.list_store_model.append(MyListModelDataItem(2, 'Bart', 'Simpson'))
        self.list_store_model.append(MyListModelDataItem(3, 'James', 'Bond'))

        self.scrolled_window = Gtk.ScrolledWindow.new()
        self.set_child(self.scrolled_window)

        # # ColumnView with custom columns
        # self.columnview = Gtk.ColumnView()
        # self.columnview.set_show_column_separators(True)
        # data = [f'Data Row: {row}' for row in range(50)]
        # for i in range(4):
        #     column = Gtk.ColumnViewColumn()
        #     column.set_title(f"Column {i}")
        #     self.columnview.append_column(column)
        # self.scrolled_window.set_child(self.columnview)


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


app = MyApp(application_id="com.example.gtk4.columnview", flags=Gio.ApplicationFlags.FLAGS_NONE)
app.run(sys.argv)
