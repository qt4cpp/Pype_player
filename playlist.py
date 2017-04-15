from PyQt5.QtCore import QUrl, QMimeData, Qt, QByteArray, QDataStream, QIODevice, QRect, QPoint
from PyQt5.QtGui import QDrag, QPixmap, QRegion
from PyQt5.QtWidgets import (QApplication, QListWidget, QFileDialog, QPushButton, QHBoxLayout,
                             QVBoxLayout, QWidget, QStyle, QAbstractItemView, QListWidgetItem)
from PyQt5.QtMultimedia import QMediaContent, QMediaResource

class Playlist(QWidget):

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)
        self.m_playlist = []
        self.playListView = PlaylistView()
        self.openButton = QPushButton('open')

        layout = QVBoxLayout()
        layout.addWidget(self.playListView)
        layout.addWidget(self.openButton)
        self.setLayout(layout)

        self.openButton.clicked.connect(self.open)

        self.show()


    def open(self):
        fileURL, _ = QFileDialog.getOpenFileUrl(self, 'Open File')

        if not fileURL.isEmpty():
            self.m_playlist.append(fileURL)
            self.playListView.addItem(fileURL.fileName())



class PlaylistView(QListWidget):

    @property
    def mime_Index(self):
        return 'application/x-original_index'


    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)

    def mousePressEvent(self, event):
        if Qt.LeftButton == event.button():
            self.dragStartPosition = event.pos()
            selectedIndex = self.indexAt(self.dragStartPosition)
            self.setCurrentIndex(selectedIndex)

    def mouseMoveEvent(self, event):
        """

        :type event: QMoveEvent
        
        """
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            return
        if self.itemAt(self.dragStartPosition) == None:
            return

        currentItem = self.currentItem()
        mimeData = QMimeData()
        mimeData.setText(currentItem.text())
        originalIndex = QByteArray()
        originalIndex.append(str(self.currentIndex().row()))
        mimeData.setData(self.mime_Index, originalIndex)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos())

        dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)

        if dropAction == Qt.MoveAction:
            delItem = self.takeItem(self.currentRow())
            del(delItem)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        print(event.pos())
        if event.mimeData().hasText():
            mime = event.mimeData()
            url = mime.text()
            print(url)
            position = event.pos()
            previousRow = mime.data(self.mime_Index)
            print(previousRow)
            self.insertItem(0, url)

            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())