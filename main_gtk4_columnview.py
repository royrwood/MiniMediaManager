import sys
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject, Gdk, GLib


class MyListModelDataItem(GObject.Object):
    __gtype_name__ = "MyListModelDataItem"

    def __init__(self, user_id, user_name_first, user_name_last):
        super().__init__()

        self.user_id = user_id
        self.user_name_first = user_name_first
        self.user_name_last = user_name_last

    # @GObject.Property(type=str)
    # def user_id(self):
    #     return self._user_id
    #
    # @GObject.Property(type=str)
    # def user_name_first(self):
    #     return self._user_name_first
    #
    # @GObject.Property(type=str)
    # def user_name_last(self):
    #     return self._user_name_last

    def __repr__(self):
        return f"MyListModelDataItem(id={self.user_id}, user_name={self.user_name_first} {self.user_name_last})"


class MyItemFactory(Gtk.SignalListItemFactory):
    def __init__(self, field_name):
        super().__init__()
        self._field_name = field_name
        self.connect("setup", self.on_setup)
        self.connect("bind", self.on_bind)

    def on_setup(self, _signal_factory, list_item):
        label = Gtk.Label.new()
        label.set_halign(Gtk.Align.START)
        list_item.set_child(label)

    def on_bind(self, _signal_factory, list_item):
        my_list_mode_data_item = list_item.props.item
        label = list_item.get_child()  # label
        label.props.label = str(getattr(my_list_mode_data_item, self._field_name))


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 600)

        self.list_store_model = Gio.ListStore(item_type=MyListModelDataItem)
        self.list_store_model.append(MyListModelDataItem(1, 'Karl', 'Barkley'))
        self.list_store_model.append(MyListModelDataItem(2, 'Bart', 'Simpson'))
        self.list_store_model.append(MyListModelDataItem(3, 'James', 'Bond'))

        # self.listview = Gtk.ListView.new(self.single_selection_list_store, self.signal_factory)

        # ColumnView with custom columns
        self.single_selection_list_store = Gtk.SingleSelection(model=self.list_store_model)
        self.single_selection_list_store.connect("notify::selected", self.on_item_list_selected)
        self.column_view = Gtk.ColumnView(model=self.single_selection_list_store, hexpand=True, vexpand=True)
        # self.column_view.set_show_column_separators(True)
        self.column_view.set_show_row_separators(True)
        self.column_view.append_column(Gtk.ColumnViewColumn(title='ID', factory=MyItemFactory('user_id'), expand=True))
        self.column_view.append_column(Gtk.ColumnViewColumn(title='FIRST', factory=MyItemFactory('user_name_first'), expand=True))
        self.column_view.append_column(Gtk.ColumnViewColumn(title='ID', factory=MyItemFactory('user_name_last'), expand=True))

        self.scrolled_window = Gtk.ScrolledWindow.new()
        self.scrolled_window.set_child(self.column_view)
        self.set_child(self.scrolled_window)

    def on_item_list_selected(self, obj, g_param_spec):
        pass
        # obj should be self.single_selection_list_store
        # g_param_spec.name should be "selected"
        # selected_item = single_selection_list_store.props.selected_item  # Gtk.StringObject
        # string_value = selected_item.props.string
        # position = single_selection_list_store.get_selected()
        # print(f"Selected String   = {string_value}")
        # print(f"Selected Position = {position}")


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
