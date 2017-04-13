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
            print(fileURL)
            self.playListView.addItem(fileURL.fileName())



class PlaylistView(QListWidget):

    @property
    def mimetype(self):
        return 'application/x-fileurl'


    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)
        self.dragSourceFlag = False

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDragDropOverwriteMode(True)


    def mousePressEvent(self, event):

        if (event.button() == Qt.LeftButton):
            self.dragStartPosition = event.pos()
            selectedIndex = self.indexAt((event.pos()))
            if selectedIndex.row() == -1:
                return
            self.setCurrentIndex(selectedIndex)
        super(PlaylistView, self).mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            return
        if self.currentItem() == None:
            return

        currentItem = self.currentItem()
        mimeData = QMimeData()
        mimeData.setText(currentItem.text())
        originalIndex = QByteArray()
        mimeData.setData('x-applicatoin/original_index',
                         originalIndex.append('%d'.format(self.currentRow())))

        itemData = QByteArray()

        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << self.currentItem()

        #mimeData.setData(self.mimetype, itemData)

        itemRect = self.visualItemRect(self.currentItem())
        pixmap = QPixmap(itemRect.width(), itemRect.height())
        renderSource = QRegion(itemRect)
        self.render(pixmap, sourceRegion=renderSource)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        dropAction = drag.exec(Qt.MoveAction)

        #super(PlaylistView, self).mouseMoveEvent(event)


  #  def dragEnterEvent(self, event):
   #     if event.mimeData().hasFormat('application/x-fileurl'):
    #        super(PlaylistView, self).dragEnterEvent(event)
    #        event.acceptProposedAction()




   # def dropEvent(self, event):
    #    print(event.source)
     #   self.playListView.addItem(event.source)
      #  super(PlaylistView, self).dropEvent(event)
       # event.acceptProposedAction()
        #print(event.source)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())