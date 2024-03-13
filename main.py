from typing import Union
import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex, QEvent
from PySide6.QtWidgets import QAbstractItemView


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

    def rowCount(self, parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = None):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, parent: Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex] = None):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
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

    @staticmethod
    def selection_changed(selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        indices = ','.join([f'({ix.column()}, {ix.row()})' for ix in selected.indexes()])
        print(f"selected: {indices}")

        indices = ','.join([f'({ix.column()}, {ix.row()})' for ix in deselected.indexes()])
        print(f"deselected: {indices}")

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
