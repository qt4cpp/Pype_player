from PyQt5.QtCore import QUrl, QMimeData, Qt, QByteArray, QDataStream, QIODevice, QModelIndex, \
    QPointF, QPoint
from PyQt5.QtGui import QDrag, QPixmap, QRegion, QBrush, QColor, QDragLeaveEvent, QLinearGradient
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
        self.setDropIndicatorShown(True)

        self.previousIndex = QModelIndex()
        self.originalBackground = QBrush()

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
        currentRow = self.currentIndex().row()
        originalIndex = QByteArray()
        originalIndex.append(str(currentRow))
        mimeData.setData(self.mime_Index, originalIndex)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos())

        dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)

        if dropAction == Qt.MoveAction:
            delItem = self.takeItem(currentRow)
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
            if self.previousIndex.row() >= 0:
                self.changeItemBackground(self.previousIndex)

            indexAtCursor = self.indexAt(event.pos())
            self.dropIndicatorlBackground(event.pos())
            #self.changeItemBackground(indexAtCursor, QColor(0,0,0,70))
            self.previousIndex = indexAtCursor
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.changeItemBackground(self.previousIndex)

    def dropEvent(self, event):

        if event.mimeData().hasText():
            mime = event.mimeData()
            url = mime.text()
            print(url)
            position = event.pos()
            previousRow = mime.data(self.mime_Index)
            print(previousRow)
            index = self.indexAt(position)
            self.changeItemBackground(index)
            self.insertItem(index.row(), url)

            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropIndicatorlBackground(self, position):
        item = self.itemAt(position)
        if item:
            rect = self.visualItemRect(item)
            gradientBrush = QLinearGradient(QPoint(rect.center().x(), 0),
                                                    QPoint(rect.center().x(), rect.height()))
            startColor = QColor(Qt.white)
            endColor = QColor(0, 0, 0, 70)
            gradientBrush.setColorAt(0, startColor)
            gradientBrush.setColorAt(1, endColor)

            item.setBackground(gradientBrush)

    def changeItemBackground(self, index, color=QColor(255,255,255)):
        item = self.itemFromIndex(index)
        if item:
            item.setBackground(QBrush(color))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())