import time
from typing import List, Text, Tuple
import dataclasses
import json
import os
import os.path
import re
import sys

from PySide6 import QtCore
from PySide6.QtCore import QEvent
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QSettings
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtCore import QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPalette
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QStyleOptionViewItem
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QLabel


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


class FolderScanWorker(QThread):
    progress_signal = Signal(str)

    def __init__(self, folder_path: Text, ignore_extensions: Text = None, filename_metadata_tokens: Text = None):
        super().__init__()
        self.folder_data = None
        self.ignore_extensions = ignore_extensions or 'png,jpg,nfo,srt'
        self.filename_metadata_tokens = filename_metadata_tokens or '480p,720p,1080p,bluray,hevc,x265,x264,web,webrip,web-dl,repack,proper,extended,remastered,dvdrip,dvd,hdtv,xvid,hdrip,brrip,dvdscr,pdtv'
        self.folder_path = folder_path
        self.keep_scanning = True

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
                self.progress_signal.emit(f'FolderScanWorker: Processing file "{filename}"')
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


def load_video_file_data(video_file_path: str) -> List[VideoFile]:
    with open(video_file_path, encoding='utf8') as f:
        video_files_json = json.load(f)

    video_files_data = list()
    for video_file_dict in video_files_json:
        video_file = VideoFile(**video_file_dict)
        video_files_data.append(video_file)

    return video_files_data


class CancellableProgressDialog(QDialog):
    def __init__(self, initial_message: str):
        super().__init__()

        self.message_label = QLabel(initial_message)
        self.cancel_button = QPushButton('Cancel')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.cancel_button)
        self.setLayout(self.layout)

        self.resize(800, 200)

    def set_message(self, message: str):
        print(f'CancellableProgressDialog: Setting label text to: {message}')
        self.message_label.setText(message)


class VerticalLineDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        # Let the base class do the rendering
        super().paint(painter, option, index)

        # And now paint the horizontal line
        line = QtCore.QLine(option.rect.bottomLeft(), option.rect.bottomRight())
        color = option.palette.color(QPalette.Dark)
        painter.save()
        painter.setPen(QPen(color))
        painter.drawLine(line)
        painter.restore()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.video_file_data = None
        self.video_file_path = None

        # The right side of the splitter is a dummy widget for now
        self.textedit = QTextEdit()

        # The left side of the splitter is a table
        self.table_widget = QTableWidget()

        # Set up table columns
        column_headers = ['Title', ' Year ', ' Rating ', ' IMDB ']
        self.table_widget.setColumnCount(len(column_headers))
        self.table_widget.setHorizontalHeaderLabels(column_headers)
        self.table_widget.setAlternatingRowColors(True)

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.table_widget.setColumnWidth(0, 200)

        # Configure table appearance and behaviour
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setShowGrid(False)
        self.table_widget.setItemDelegate(VerticalLineDelegate(self.table_widget))
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.selectRow(0)
        self.table_widget.setFocus()

        # Set up callbacks
        self.table_widget.installEventFilter(self)
        self.table_widget.selectionModel().selectionChanged.connect(self.selection_changed)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.table_widget)
        self.splitter.addWidget(self.textedit)
        self.splitter.setSizes([200, 100])

        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addStretch(1)
        self.button_load_json = QPushButton("Load JSON")
        self.hbox_layout.addWidget(self.button_load_json)
        self.button_load_json.pressed.connect(self.load_json_clicked)
        self.hbox_layout.addSpacing(20)
        self.scan_folder_button = QPushButton("Scan Folder")
        self.hbox_layout.addWidget(self.scan_folder_button)
        self.scan_folder_button.pressed.connect(self.scan_folder_clicked)
        self.hbox_layout.addSpacing(20)
        self.button_save_json = QPushButton("Save JSON")
        self.hbox_layout.addWidget(self.button_save_json)
        self.button_save_json.pressed.connect(self.save_json_clicked)
        self.hbox_layout.addSpacing(20)
        self.button_show_progress = QPushButton("Show Progress")
        self.hbox_layout.addWidget(self.button_show_progress)
        self.button_show_progress.pressed.connect(self.show_progress_clicked)
        self.hbox_layout.addSpacing(20)
        self.button_hide_progress = QPushButton("Hide Progress")
        self.hbox_layout.addWidget(self.button_hide_progress)
        self.button_hide_progress.pressed.connect(self.hide_progress_clicked)

        self.vbox_layout = QVBoxLayout()
        self.vbox_layout.addWidget(self.splitter)
        self.vbox_layout.addLayout(self.hbox_layout)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vbox_layout)
        self.setCentralWidget(self.central_widget)

        # Get last saved size of window
        settings = QSettings('MiniMediaManager', 'MiniMediaManager')

        size: QSize = settings.value("size")
        if size:
            self.resize(size)
        else:
            window_size = QGuiApplication.primaryScreen().availableGeometry().size()
            self.resize(window_size * 0.7)

        pos: QSize = settings.value("pos")
        if pos:
            self.move(pos)  # Does not seem to work on Wayland

        self.progress_dialog = CancellableProgressDialog('Initial Text!')
        self.progress_dialog.cancel_button.pressed.connect(self.do_stop_scanning)
        self.folder_scan_worker = None

    def closeEvent(self, event):
        print('Main window closing!')
        settings = QSettings('MiniMediaManager', 'MiniMediaManager')
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    # def moveEvent(self, event: QMoveEvent):
    #     print("moveEvent: x=`{}`, y=`{}`".format(event.pos().x(), event.pos().y()))
    #     super().moveEvent(event)
    #
    # def resizeEvent(self, event: QResizeEvent):
    #     print("resizeEvent: w=`{}`, h=`{}`".format(event.size().width(), event.size().height()))
    #     super().resizeEvent(event)

    @staticmethod
    def selection_changed(selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        selected_rows = {ix.row() for ix in selected.indexes()}
        print(f"selected: {selected_rows}")

        # deselected_rows = {ix.row() for ix in deselected.indexes()}
        # print(f"deselected: {deselected_rows}")

    def eventFilter(self, watched: QtCore.QObject, event: QEvent):
        if event.type() == QEvent.KeyPress and watched is self.table_widget:
            key = event.key()
            if key == Qt.Key_Escape:
                print('escape')
            elif key == Qt.Key_Return:
                print('return')
        return QWidget.eventFilter(self, watched, event)

    def update_table_widget(self):
        if not self.video_file_data:
            return

        # column_headers = ['Title', ' Year ', ' Rating ', ' IMDB ']
        self.table_widget.setRowCount(len(self.video_file_data))
        for row_index, video_file in enumerate(self.video_file_data):
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(video_file.scrubbed_file_name))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(video_file.scrubbed_file_year))
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(video_file.imdb_rating))
            self.table_widget.setItem(row_index, 2, QTableWidgetItem(video_file.imdb_tt))

    def load_json_clicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("*.json")
        if dialog.exec() and (selected_files := dialog.selectedFiles()):
            self.video_file_path = selected_files[0]
            with open(self.video_file_path, encoding='utf8') as f:
                video_files_json = json.load(f)

            self.video_file_data = list()
            for video_file_dict in video_files_json:
                video_file = VideoFile(**video_file_dict)
                self.video_file_data.append(video_file)

            self.update_table_widget()

    def save_json_clicked(self):
        if not self.video_file_path:
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setNameFilter("*.json")

            # TODO: Save As?
            # dir_name = os.path.dirname(self.video_file_path)
            # file_name = os.path.basename(self.video_file_path)
            # dialog.setDirectory(dir_name)
            # dialog.selectFile(file_name)

            if dialog.exec() and (selected_files := dialog.selectedFiles()):
                self.video_file_path = selected_files[0]

        if self.video_file_path:
            with open(self.video_file_path, 'w', encoding='utf8') as f:
                json_list = [dataclasses.asdict(video_file) for video_file in self.video_file_data]
                json_str = json.dumps(json_list, indent=4)
                f.write(json_str)

    def scan_folder_clicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        # dialog.setDirectory(os.path.expanduser('~'))
        if dialog.exec() and (selected_files := dialog.selectedFiles()):
            chosen_directory = selected_files[0]
            print('Creating FolderScanWorker...')
            self.folder_scan_worker = FolderScanWorker(folder_path=chosen_directory)
            self.folder_scan_worker.progress_signal.connect(self.do_progress_update)
            self.folder_scan_worker.started.connect(self.show_progress_clicked)
            self.folder_scan_worker.finished.connect(self.hide_progress_clicked)
            print('Starting FolderScanWorker...')
            self.folder_scan_worker.start()
            print('Started FolderScanWorker')
            # self.video_file_data = scan_folder(chosen_directory)
            # self.update_table_widget()

    def show_progress_clicked(self):
        self.progress_dialog.show()

    def hide_progress_clicked(self):
        self.progress_dialog.hide()

    def do_progress_update(self, message):
        self.progress_dialog.set_message(message)

    def do_stop_scanning(self):
        if self.folder_scan_worker:
            self.folder_scan_worker.stop_scanning()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
