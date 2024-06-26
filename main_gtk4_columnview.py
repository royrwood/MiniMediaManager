from threading import Thread
from typing import List, Text, Tuple, Callable
import dataclasses
import json
import os
import os.path
import re
import sys
import threading
import time

import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GObject, Gdk, GLib, Adw


@dataclasses.dataclass
class VideoFile:
    file_path: Text = ''
    scrubbed_file_name: Text = ''
    scrubbed_file_year: Text = ''
    imdb_tt: Text = ''
    imdb_name: Text = ''
    imdb_year: Text = ''
    imdb_rating: Text = ''
    imdb_genres: List[Text] = None
    imdb_plot: Text = None
    is_dirty: bool = False


class FolderScanWorker(Thread):
    def __init__(self, folder_path: Text, ignore_extensions: Text = None, filename_metadata_tokens: Text = None, progress_callback: Callable = None):
        super().__init__()
        self.folder_data = None
        self.ignore_extensions = ignore_extensions or 'png,jpg,nfo,srt'
        self.filename_metadata_tokens = filename_metadata_tokens or '480p,720p,1080p,bluray,hevc,x265,x264,web,webrip,web-dl,repack,proper,extended,remastered,dvdrip,dvd,hdtv,xvid,hdrip,brrip,dvdscr,pdtv'
        self.folder_path = folder_path
        self.keep_scanning = True
        self.progress_callback = progress_callback

    def stop_scanning(self):
        self.keep_scanning = False

    @staticmethod
    def scrub_video_file_name(file_name: Text, filename_metadata_tokens: Text) -> Tuple[Text, Text]:
        year = ''

        match = re.match(r'((.*)\((\d{4})\))', file_name)
        if match:
            file_name = match.group(2)
            year = match.group(3)
            scrubbed_file_name_list = file_name.replace('.', ' ').split()

        else:
            metadata_token_list = [token.lower().strip() for token in filename_metadata_tokens.split(',')]
            file_name_parts = file_name.replace('.', ' ').split()
            scrubbed_file_name_list = list()

            for file_name_part in file_name_parts:
                file_name_part = file_name_part.lower()

                if file_name_part in metadata_token_list:
                    break
                scrubbed_file_name_list.append(file_name_part)

            if scrubbed_file_name_list:
                match = re.match(r'\(?(\d{4})\)?', scrubbed_file_name_list[-1])
                if match:
                    year = match.group(1)
                    del scrubbed_file_name_list[-1]

        scrubbed_file_name = ' '.join(scrubbed_file_name_list).strip()
        scrubbed_file_name = re.sub(' +', ' ', scrubbed_file_name)
        return scrubbed_file_name, year

    def run(self):
        print(f'FolderScanWorker: Begin processing directory "{self.folder_path}"')

        ignore_extensions_list = [ext.lower().strip() for ext in self.ignore_extensions.split(',')]

        self.folder_data = list()

        for dir_path, dirs, files in os.walk(self.folder_path):
            for filename in files:
                if self.keep_scanning is False:
                    print(f'FolderScanWorker: Stopping scanning')
                    return

                print(f'FolderScanWorker: Processing file "{filename}"')
                GLib.idle_add(self.progress_callback, f'FolderScanWorker: Processing file "{filename}"')
                time.sleep(1.0)

                file_path = os.path.join(dir_path, filename)
                filename_parts = os.path.splitext(filename)
                filename_no_extension = filename_parts[0]
                filename_extension = filename_parts[1]
                if filename_extension.startswith('.'):
                    filename_extension = filename_extension[1:]

                if filename_extension.lower() in ignore_extensions_list:
                    continue

                scrubbed_video_file_name, year = self.scrub_video_file_name(filename_no_extension, self.filename_metadata_tokens)
                video_file = VideoFile(file_path=file_path, scrubbed_file_name=scrubbed_video_file_name, scrubbed_file_year=year)
                self.folder_data.append(video_file)

        print(f'FolderScanWorker: End processing directory "{self.folder_path}"')


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

        # self.list_store_model = Gio.ListStore(item_type=MyListModelDataItem)
        # self.list_store_model.append(MyListModelDataItem(1, 'Karl', 'Barkley'))
        # self.list_store_model.append(MyListModelDataItem(2, 'Bart', 'Simpson'))
        # self.list_store_model.append(MyListModelDataItem(3, 'James', 'Bond'))
        #
        # # self.listview = Gtk.ListView.new(self.single_selection_list_store, self.signal_factory)
        #
        # # ColumnView with custom columns
        # self.single_selection_list_store = Gtk.SingleSelection(model=self.list_store_model)
        # self.single_selection_list_store.connect("notify::selected", self.on_item_list_selected)
        # self.column_view = Gtk.ColumnView(model=self.single_selection_list_store, hexpand=True, vexpand=True)
        # # self.column_view.set_show_column_separators(True)
        # self.column_view.set_show_row_separators(True)
        # self.column_view.append_column(Gtk.ColumnViewColumn(title='ID', factory=MyItemFactory('user_id'), expand=True))
        # self.column_view.append_column(Gtk.ColumnViewColumn(title='FIRST', factory=MyItemFactory('user_name_first'), expand=True))
        # self.column_view.append_column(Gtk.ColumnViewColumn(title='ID', factory=MyItemFactory('user_name_last'), expand=True))
        #
        # self.scrolled_window = Gtk.ScrolledWindow.new()
        # self.scrolled_window.set_child(self.column_view)
        # self.set_child(self.scrolled_window)

        # self.progress = Gtk.ProgressBar(show_text=True)
        # self.set_child(self.progress)

        # thread = threading.Thread(target=self.example_target)
        # thread.daemon = True
        # thread.start()
        #
        # thread = FolderScanWorker(folder_path='/home/rrwood/Downloads/ZZ_Movies_Copied_To_External/', progress_callback=self.update_progress)
        # thread.daemon = True
        # thread.start()

        button = Gtk.Button(label="Open dialog")
        button.connect("clicked", self.on_button_clicked)

        # self.dialog = Gtk.AlertDialog(message='Main Message', buttons=['Cancel'])

        self.message_dialog = Gtk.MessageDialog(text='This is the main text', secondary_text='This is the secondary text', buttons=Gtk.ButtonsType.CANCEL)
        self.message_dialog.connect("response", self.message_dialog_response)
        self.message_dialog.set_transient_for(self)
        self.message_dialog.set_modal(False)

        # self.progress_window = Gtk.Window()
        # self.progress_window.set_default_size(400, 200)
        # self.progress_window_box = Gtk.Box(vexpand=True, spacing=20, orientation=Gtk.Orientation.VERTICAL, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        # self.progress_window.set_child(self.progress_window_box)
        # self.progress_window_label = Gtk.Label(label='This is some text')
        # self.progress_window_box.append(self.progress_window_label)
        # self.progress_window_box.append(Gtk.Box(vexpand=True))
        # self.progress_window_button = Gtk.Button(label='Cancel', hexpand=False, halign=Gtk.Align.END)
        # self.progress_window_box.append(self.progress_window_button)

        self.set_child(button)


    # def update_progress(self, progress_message):
    #     self.progress.pulse()
    #     self.progress.set_text(progress_message)
    #     return False
    #
    # def example_target(self):
    #     for i in range(50):
    #         GLib.idle_add(self.update_progress, i)
    #         time.sleep(0.2)

    def on_item_list_selected(self, obj, g_param_spec):
        pass
        # obj should be self.single_selection_list_store
        # g_param_spec.name should be "selected"
        # selected_item = single_selection_list_store.props.selected_item  # Gtk.StringObject
        # string_value = selected_item.props.string
        # position = single_selection_list_store.get_selected()
        # print(f"Selected String   = {string_value}")
        # print(f"Selected Position = {position}")

    # def on_button_clicked(self, widget):
    #     dialog = Gtk.Dialog()
    #     # dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
    #     dialog.set_default_size(150, 100)
    #     content_area = dialog.get_content_area()
    #     content_area.append(Gtk.Label(label='This is a dialog box'))
    #     dialog.add_button('Dialog Button', 0)
    #     dialog.show()

    def on_button_clicked(self, widget):
        # dialog = Gtk.AlertDialog(message='Main Message', detail='Secondary Message', buttons=['Cancel'])
        # dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        # dialog.set_default_size(150, 100)

        thread = FolderScanWorker(folder_path='/home/rrwood/Downloads/ZZ_Movies_Copied_To_External/', progress_callback=self.on_dialog_progress_update)
        thread.daemon = True
        thread.start()

        # self.dialog.choose(self, None, self.dialog_choose_callback, 'My User Data')

        # self.adw_dialog.choose(None, self.on_dialog_cancel, 'My User Data')

        self.message_dialog.show()

        # self.progress_window.present()
        #
        # dialog = Gtk.AlertDialog(message='Main Message', buttons=['Cancel'])
        # dialog.choose(self, None, self.on_dialog_cancel, 'My User Data')

    def on_dialog_progress_update(self, progress_message):
        print(f'on_dialog_progress_update: {progress_message}')

        box: Gtk.Widget = self.message_dialog.get_message_area()
        if isinstance(box, Gtk.Box):
            child: Gtk.Widget = box.get_first_child()
            if child and isinstance(child, Gtk.Widget):
                child = child.get_next_sibling()
                if child and isinstance(child, Gtk.Label):
                    child.set_label(progress_message)

        # self.progress_window_label.set_label(progress_message)

        # foo = self.message_dialog.get_child()

        # self.adw_dialog.set_body(progress_message)
        # self.progress_window_label.set_label(progress_message)

        pass

    # def dialog_choose_callback(self, _g_object, g_async_result, _g_pointer_data):
    #     self.message_dialog.destroy()
    #     pass

    def message_dialog_response(self, g_object, g_async_result):
        self.message_dialog.destroy()
        pass

        #     # result = g_object.choose_finish(g_async_result)
        #     self.message_dialog.destroy()
        #     pass
    # def on_dialog_cancel(self, g_object, g_async_result):
    #     # result = g_object.choose_finish(g_async_result)
    #     self.message_dialog.destroy()
    #     pass


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
