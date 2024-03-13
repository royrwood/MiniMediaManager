from typing import Union
import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex, QEvent, QSize
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtGui import QGuiApplication

# class MyTableView(QtWidgets.QTableView):
#     def __init__(self, parent=None):
#         super().__init__(parent)


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = None):
        super(TableModel, self).__init__(parent)
        self._data = data

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        else:
            # DisplayRole: Qt.ItemDataRole = ...  # 0x0
            # DecorationRole: Qt.ItemDataRole = ...  # 0x1
            # EditRole: Qt.ItemDataRole = ...  # 0x2
            # ToolTipRole: Qt.ItemDataRole = ...  # 0x3
            # StatusTipRole: Qt.ItemDataRole = ...  # 0x4
            # WhatsThisRole: Qt.ItemDataRole = ...  # 0x5
            # FontRole: Qt.ItemDataRole = ...  # 0x6
            # TextAlignmentRole: Qt.ItemDataRole = ...  # 0x7
            # BackgroundRole: Qt.ItemDataRole = ...  # 0x8
            # ForegroundRole: Qt.ItemDataRole = ...  # 0x9
            # CheckStateRole: Qt.ItemDataRole = ...  # 0xa
            # AccessibleTextRole: Qt.ItemDataRole = ...  # 0xb
            # AccessibleDescriptionRole: Qt.ItemDataRole = ...  # 0xc
            # SizeHintRole: Qt.ItemDataRole = ...  # 0xd
            # InitialSortOrderRole: Qt.ItemDataRole = ...  # 0xe
            # DisplayPropertyRole: Qt.ItemDataRole = ...  # 0x1b
            # DecorationPropertyRole: Qt.ItemDataRole = ...  # 0x1c
            # ToolTipPropertyRole: Qt.ItemDataRole = ...  # 0x1d
            # StatusTipPropertyRole: Qt.ItemDataRole = ...  # 0x1e
            # WhatsThisPropertyRole: Qt.ItemDataRole = ...  # 0x1f
            # UserRole: Qt.ItemDataRole = ...  # 0x100
            pass

    def rowCount(self, parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = None):
        return len(self._data)

    def columnCount(self, parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = None):
        return len(self._data[0])


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()
        # self.table = MyTableView()
        self.table.installEventFilter(self)

        data = [[f'Line {i}'] + [j for j in range(1, 20)] for i in range(1, 100)]

        self.model = TableModel(data)
        self.table.setModel(self.model)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.selectRow(0)
        self.table.setFocus()
        self.table.setShowGrid(False)
        self.table.setStyleSheet('QTableView::item {border-bottom: 1px solid #d6d9dc;}')

        self.setCentralWidget(self.table)

        selection_model = self.table.selectionModel()
        selection_model.selectionChanged.connect(self.selection_changed)

        window_size = QGuiApplication.primaryScreen().availableGeometry().size()
        self.resize(window_size * 0.7)

    def closeEvent(self, event):
        print('Main window closing!')

    @staticmethod
    def selection_changed(selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        selected_rows = {ix.row() for ix in selected.indexes()}
        print(f"selected: {selected_rows}")

        # deselected_rows = {ix.row() for ix in deselected.indexes()}
        # print(f"deselected: {deselected_rows}")

    def eventFilter(self, watched: QtCore.QObject, event: QEvent):
        if event.type() == QEvent.KeyPress and watched is self.table:
            key = event.key()
            if key == Qt.Key_Escape:
                print('escape')
            elif key == Qt.Key_Return:
                print('return')
        return QtWidgets.QWidget.eventFilter(self, watched, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


# Get/Set window size, position between runs?
#
# def readSettings(self):
#     settings = QSettings("Trolltech", "Application Example")
#     pos = settings.value("pos", QPoint(200, 200))
#     size = settings.value("size", QSize(400, 400))
#     self.resize(size)
#     self.move(pos)
#
# def writeSettings(self):
#     settings = QSettings("Trolltech", "Application Example")
#     settings.setValue("pos", self.pos())
#     settings.setValue("size", self.size())