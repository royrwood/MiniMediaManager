import sys

from PySide6 import QtCore
from PySide6.QtCore import Qt, QEvent, QSize, QSettings, QModelIndex
from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QMainWindow, QTableWidgetItem, QApplication, QWidget, QStyledItemDelegate, QStyleOptionViewItem, QSplitter, QTextEdit
from PySide6.QtGui import QGuiApplication, QPalette, QPen, QPainter


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

        # The right side of the splitter is a dummy widget for now
        self.textedit = QTextEdit()

        # The left side of the splitter is a table
        self.table_widget = QTableWidget()

        # Add some dummy data
        num_rows = 100
        num_columns = 20
        self.table_widget.setRowCount(num_rows)
        self.table_widget.setColumnCount(num_columns)

        for row_index in range(num_rows):
            for col_index in range(num_columns):
                item = QTableWidgetItem(f'{col_index}-{row_index}')
                self.table_widget.setItem(row_index, col_index, item)

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
        self.setCentralWidget(self.splitter)

        self.splitter.addWidget(self.table_widget)
        self.splitter.addWidget(self.textedit)
        self.splitter.setSizes([200, 100])

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
