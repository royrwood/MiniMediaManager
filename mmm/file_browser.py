from typing import List

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject, GLib

from mmm.file_scanner import VideoFile, load_video_file_data


class MyListModelDataItem(GObject.Object):
    # __gtype_name__ = "MyListModelDataItem"

    def __init__(self, title, year, rating, imdb_tt):
        super().__init__()

        self.title = title
        self.year = year
        self.rating = rating
        self.imdb_tt = imdb_tt


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
        attr = getattr(my_list_mode_data_item, self._field_name)
        label.props.label = str(attr)


class FileBrowserPanel(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, vexpand=True, hexpand=True, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10, *args, **kwargs)

        self.video_file_data: List[VideoFile] = None

        # self.list_store_model = Gio.ListStore(item_type=MyListModelDataItem)
        self.list_store_model = Gio.ListStore()

        # ColumnView with custom columns
        self.single_selection_list_store = Gtk.SingleSelection(model=self.list_store_model)
        self.single_selection_list_store.connect("notify::selected", self.on_item_list_selected)
        self.column_view = Gtk.ColumnView(model=self.single_selection_list_store, hexpand=True, vexpand=True)
        self.column_view.set_show_row_separators(True)
        self.column_view.append_column(Gtk.ColumnViewColumn(title='TITLE', factory=MyItemFactory('title'), expand=True))
        self.column_view.append_column(Gtk.ColumnViewColumn(title='YEAR', factory=MyItemFactory('year'), expand=True))
        self.column_view.append_column(Gtk.ColumnViewColumn(title='RATING', factory=MyItemFactory('rating'), expand=True))
        self.column_view.append_column(Gtk.ColumnViewColumn(title='IMDB TT', factory=MyItemFactory('imdb_tt'), expand=True))

        self.column_view_scrolled_window = Gtk.ScrolledWindow.new()
        self.column_view_scrolled_window.set_child(self.column_view)

        self.scrolled_window_button = Gtk.Button(label='Load', hexpand=True, vexpand=False)
        self.scrolled_window_button.connect("clicked", self.on_load_video_json)

        self.details_poster = Gtk.Picture(file=Gio.File.new_for_path('poster.png'), halign=Gtk.Align.START, valign=Gtk.Align.START)

        self.details_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        self.details_title_label = Gtk.Label(label='Title: ', halign=Gtk.Align.START)
        self.details_year_label = Gtk.Label(label='Year: ', halign=Gtk.Align.START)
        self.details_rating_label = Gtk.Label(label='Rating: ', halign=Gtk.Align.START)
        self.details_vbox.append(self.details_title_label)
        self.details_vbox.append(self.details_year_label)
        self.details_vbox.append(self.details_rating_label)

        self.details_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True, hexpand=True, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
        self.details_hbox.append(self.details_poster)
        self.details_hbox.append(self.details_vbox)

        self.file_browser_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True, wide_handle=True)
        self.file_browser_paned.set_start_child(self.column_view_scrolled_window)
        self.file_browser_paned.set_end_child(self.details_hbox)

        self.append(self.file_browser_paned)
        self.append(self.scrolled_window_button)

    # def file_added_handler(self, instance, filename):
    #     print(f'MainWindow:file_added_handler: {filename}')

    def on_load_video_json(self, _widget):
        def open_dialog_open_callback(source_object, result, _data):
            try:
                gio_file: Gio.File = source_object.open_finish(result)
                if gio_file is not None:
                    print(f"File path is {gio_file.get_path()}")
                    self.video_file_data = load_video_file_data(gio_file.get_path())
                    if self.video_file_data:
                        self.list_store_model.remove_all()
                        for video_file in self.video_file_data:
                            file_name = video_file.imdb_name or video_file.scrubbed_file_name
                            file_year = video_file.imdb_year or video_file.scrubbed_file_year
                            imdb_rating = video_file.imdb_rating
                            imdb_tt = video_file.imdb_tt
                            self.list_store_model.append(MyListModelDataItem(file_name, file_year, imdb_rating, imdb_tt))
            except GLib.Error as error:
                print(f"Error opening file: {error.message}")

        open_dialog = Gtk.FileDialog(title="Select a File")
        open_dialog.open(None, None, open_dialog_open_callback, None)

    def on_item_list_selected(self, obj, g_param_spec):
        # selected_item = self.single_selection_list_store.props.selected_item

        position = self.single_selection_list_store.get_selected()
        selected_item = self.video_file_data[position]
        self.details_title_label.set_label(f'Title: {selected_item.imdb_name}')
        self.details_year_label.set_label(f'Year: {selected_item.imdb_year}')
        self.details_rating_label.set_label(f'Rating: {selected_item.imdb_rating}')

        pass

        # obj should be self.single_selection_list_store
        # g_param_spec.name should be "selected"
        # selected_item = self.single_selection_list_store.props.selected_item  # Gtk.StringObject
        # string_value = selected_item.props.string
        # position = self.single_selection_list_store.get_selected()
        # print(f"Selected String   = {string_value}")
        # print(f"Selected Position = {position}")
