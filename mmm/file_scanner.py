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
from gi.repository import Gtk, Gio, GObject, Gdk, GLib


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


def load_video_file_data(video_file_path: str) -> List[VideoFile]:
    with open(video_file_path, encoding='utf8') as f:
        video_files_json = json.load(f)

    video_files_data = list()
    for video_file_dict in video_files_json:
        video_file = VideoFile(**video_file_dict)
        video_files_data.append(video_file)

    return video_files_data


class FolderScanWorker(Thread):
    def __init__(self, folder_path: Text, ignore_extensions: Text = None, filename_metadata_tokens: Text = None, progress_callback: Callable = None, complete_callback: Callable = None):
        super().__init__(daemon=True)
        self.folder_data = None
        self.ignore_extensions = ignore_extensions or 'png,jpg,nfo,srt'
        self.filename_metadata_tokens = filename_metadata_tokens or '480p,720p,1080p,bluray,hevc,x265,x264,web,webrip,web-dl,repack,proper,extended,remastered,dvdrip,dvd,hdtv,xvid,hdrip,brrip,dvdscr,pdtv'
        self.folder_path = folder_path
        self.keep_scanning = True
        self.progress_callback = progress_callback
        self.complete_callback = complete_callback

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
                GLib.idle_add(self.progress_callback, filename)
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

        if self.complete_callback:
            print(f'FolderScanWorker: Scheduling self.complete_callback')
            GLib.idle_add(self.complete_callback, self.folder_path)


class FileScannerPanel(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, vexpand=True, hexpand=True, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10, *args, **kwargs)

        self.file_scanning_thread = FolderScanWorker(folder_path='/home/rrwood/Downloads/ZZ_Movies_Copied_To_External/', progress_callback=self.on_scanning_progress, complete_callback=self.on_scanning_complete)
        # thread.start()

        self.progress_log_text_buffer = Gtk.TextBuffer()
        text_buffer_end_iter = self.progress_log_text_buffer.get_end_iter()
        self.text_buffer_mark_end: Gtk.TextMark = self.progress_log_text_buffer.create_mark("", text_buffer_end_iter, False)
        self.progress_log_text_view = Gtk.TextView(buffer=self.progress_log_text_buffer, editable=False, monospace=True, wrap_mode=Gtk.WrapMode.NONE, vexpand=True, hexpand=True, margin_top=5, margin_bottom=5, margin_start=5, margin_end=5)
        self.progress_log_text_scrolled_window = Gtk.ScrolledWindow(has_frame=True)
        self.progress_log_text_scrolled_window.set_child(self.progress_log_text_view)

        self.file_scanning_start_button = Gtk.Button(label='Start', hexpand=True, vexpand=False)
        self.file_scanning_start_button.connect("clicked", self.on_start_scanning)
        self.file_scanning_pause_button = Gtk.Button(label='Pause', hexpand=True, vexpand=False)
        # self.file_scanning_pause_button.connect("clicked", self.on_show_scroll_info)
        self.file_scanning_cancel_button = Gtk.Button(label='Cancel', hexpand=True, vexpand=False)
        self.file_scanning_button_box = Gtk.Box(vexpand=False, spacing=10, orientation=Gtk.Orientation.HORIZONTAL)
        self.file_scanning_button_box.append(self.file_scanning_start_button)
        self.file_scanning_button_box.append(self.file_scanning_pause_button)
        self.file_scanning_button_box.append(self.file_scanning_cancel_button)

        self.append(self.progress_log_text_scrolled_window)
        self.append(self.file_scanning_button_box)

    @GObject.Signal(arg_types=(str,))
    def file_added(self, *args):
        pass

    @GObject.Signal(arg_types=(str,))
    def file_scanning_complete(self, *args):
        pass

    def on_start_scanning(self, _widget):
        self.file_scanning_thread.start()
        pass

    # def on_show_scroll_info(self, message):
    #     visible_rect: Gdk.Rectangle = self.file_scanning_text_view.get_visible_rect()
    #     visible_rect_top = visible_rect.y
    #     visible_rect_bottom = visible_rect_top + visible_rect.height
    #     text_buffer_end_iter = self.file_scanning_text_buffer.get_end_iter()
    #     end_line_top, end_line_height = self.file_scanning_text_view.get_line_yrange(text_buffer_end_iter)
    #     end_line_bottom = end_line_top + end_line_height
    #
    #     end_line_visible = visible_rect.y <= end_line_top <= visible_rect.y + visible_rect.height
    #
    #     print(f'end_line_top={end_line_top} end_line_bottom={end_line_bottom} visible_rect_top={visible_rect_top} visible_rect_bottom={visible_rect_bottom} end_line_visible={end_line_visible}')

    def on_scanning_progress(self, message):
        print(f'on_scanning_progress: {message}')

        self.emit('file_added', message)

        visible_rect: Gdk.Rectangle = self.progress_log_text_view.get_visible_rect()
        text_buffer_end_iter = self.progress_log_text_buffer.get_end_iter()
        end_line_top, _end_line_height = self.progress_log_text_view.get_line_yrange(text_buffer_end_iter)
        end_line_visible = visible_rect.y <= end_line_top <= visible_rect.y + visible_rect.height

        self.progress_log_text_buffer.insert(text_buffer_end_iter, message)
        self.progress_log_text_buffer.insert(text_buffer_end_iter, '\n')

        if end_line_visible:
            self.progress_log_text_view.scroll_to_mark(self.text_buffer_mark_end, 0, False, 0, 0)

        pass

    def on_scanning_complete(self, message):
        print(f'on_scanning_complete: {message}')

        self.emit('file_scanning_complete', message)
