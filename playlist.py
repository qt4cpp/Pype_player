from PyQt5.QtCore import QUrl, QMimeData, Qt, QByteArray, QDir, QModelIndex, QPoint
from PyQt5.QtGui import QDrag, QPixmap, QRegion, QBrush, QColor, QDragLeaveEvent, QLinearGradient
from PyQt5.QtWidgets import (QApplication, QFileDialog, QPushButton, QHBoxLayout,
                             QVBoxLayout, QWidget, QAbstractItemView, QPushButton, QListView)

from playlistmodel import PlaylistModel

class Playlist(QWidget):

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)

        self.playListView = PlaylistView()
        self.m_playlist: PlaylistModel = PlaylistModel()
        self.playListView.setModel(self.m_playlist)

        layout = QVBoxLayout()
        layout.addWidget(self.playListView)
        self.setLayout(layout)

        self.show()

    def debugUI(self):
        self.openButton = QPushButton('open')
        self.debugButton = QPushButton('m_playlist')

        layout = self.layout()
        layout.addWidget(self.openButton)
        layout.addWidget(self.debugButton)

        self.openButton.clicked.connect(self.open)
        self.debugButton.clicked.connect(self.debug_m_playlist)

    def open(self):
        fileURL, _ = QFileDialog.getOpenFileUrl(
            self, 'Open File', QDir.homePath(), '*.mp4 *.m4v *.mov *.mpg *.mpeg *.mp3 *.m4a *.wmv')

        if not fileURL.isEmpty():
            self.m_playlist.add_url(fileURL)

    def url(self, index=0):
        return self.playListView.m_playlist[index]

    def debug_m_playlist(self):
        print('rowCount: ', self.m_playlist.rowCount())
        for row in range(self.m_playlist.rowCount()):
            index = self.m_playlist.index(row, 0, QModelIndex())
            print('m_playlist:\n', self.m_playlist.data(index, Qt.DisplayRole))


class PlaylistView(QListView):

    @property
    def mime_Index(self):
        return 'application/x-original_index'
    @property
    def mime_URL(self):
        return 'application/x-file-url'

    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)

        self.previousIndex = QModelIndex()
        self.originalBackground = QBrush()

    def addUrl(self, url: QUrl, index=-1):
        if url.isEmpty():
            return
        file_name = url.fileName()

        if index < 0:
            self.m_playlist.append(url)
            self.addItem(file_name)
        else:
            self.m_playlist.insert(index, url)
            self.insertItem(index, file_name)

    def delUrl(self, index):
        if index < 0:
            index = self.count()-1

        delItem = self.takeItem(index)
        del(delItem)
        self.m_playlist.pop(index)

    def url(self, index:int) -> str:
        return self.m_playlist[index]

    def currentUrl(self):
        return self.m_playlist[self.currentIndex().row()]

    def nextUrl(self):
        nextIndex = self.currentIndex().row() + 1
        if nextIndex < self.count():
            return self.m_playlist[nextIndex]
        else:
            return None

    def mousePressEvent(self, event):
        """左クリックされたらカーソル下にある要素を選択し、ドラッグを認識するために現在の位置を保存する。
        :param event: QMousePressEvent
        :return: nothing
        """
        if Qt.LeftButton == event.button():
            self.dragStartPosition = event.pos()
            selectedIndex = self.indexAt(self.dragStartPosition)
            self.setCurrentIndex(selectedIndex)

    def mouseMoveEvent(self, event):
        """start Drag and prepare for Drop.

        :type event: QMoveEvent
        マウスを動かした嶺がQApplication.startDragDistance()を超えると、Drag開始されたと認識し、
        そのための準備を行う。QMimeDataを使って、データをやりとりする。
        """
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < \
                QApplication.startDragDistance():
            return
        if self.itemAt(self.dragStartPosition) is None:
            return

        currentItem = self.currentItem()
        currentRow = self.currentIndex().row()
        originalIndex = QByteArray()
        originalIndex.append(str(currentRow))
        urls = []
        urls.append(self.m_playlist[currentRow])

        mimeData = QMimeData()
        mimeData.setText(currentItem.text())
        mimeData.setData(self.mime_Index, originalIndex)
        mimeData.setUrls(urls)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos())

        dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)

    def dragEnterEvent(self, event):
        """ドラッグした状態でWidgetに入った縁で呼ばれる関数。
        :param event: QDragEvent
        :return: nothing
        
        イベントが発生元と発生しているWidgetが同一の場合はMoveActionにする。それ以外はCopyAction。
        その二つの場合は受け入れられるように、accept()もしくはacceptProposedAction()を呼ぶ。
        """

        if event.mimeData().hasText():
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """ドラッグした状態でWidget内を移動したときに呼ばれる。
        :param event: QDragMoveEvent
        :return: nothing
        
        ドラッグしている要素の背景の色を変えて、どこにファイルがDropされるかをグラデーションした背景で
        表現する。
        """
        if event.mimeData().hasText():
            if self.previousIndex.row() >= 0:
                self.changeItemBackground(self.previousIndex)

            self.dropIndicatorlBackground(event.pos())
            self.previousIndex = self.indexAt(event.pos())
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        """ドラッグしたままWidget内を出たときにドラッグ下にあった要素の背景色の色を元に戻す。
        :param event: QDragLeaveEvent
        :return: nothing
        """
        self.changeItemBackground(self.previousIndex)

    def dropEvent(self, event):
        """Dropされたらデータを取り出して、新たに登録する。
        :param event: QDropEvent
        :return: nothing
        
        ファイルへのパスと移動前に登録してあった要素のindexを取り出す。
        """

        if event.mimeData().hasText():
            mime = event.mimeData()
            file_name = mime.text()
            position = event.pos()
            previousRow = int(mime.data(self.mime_Index))
            url = QUrl(mime.urls()[0])
            index = self.indexAt(position)
            self.changeItemBackground(index)

            if self.isUpperHalfInItem(position):
                insertRow = index.row()
            else:
                insertRow = index.row()+1
            self.addUrl(url, insertRow)

            if event.source() is self:
                if previousRow < index.row():
                    self.delUrl(previousRow)
                else:
                    self.delUrl(previousRow+1)
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropIndicatorlBackground(self, position):
        """dropIndicatorを表現するために要素の背景をグラデーションにする。
        :param position: QPoint
        :return: 
        
        positionから要素を取り出し、上から下にグラデーションがかかるようにする。
        要素の半分上だと上に挿入するので、上が黒くなるようにして、
        下半分だとその逆。
        """
        item = self.itemAt(position)
        if item:
            rect = self.visualItemRect(item)
            gradientBrush = QLinearGradient(QPoint(rect.center().x(), 0),
                                                    QPoint(rect.center().x(), rect.height()))
            brightColor = QColor(Qt.white)
            darkColor= QColor(0, 0, 0, 50)
            if self.isUpperHalfInItem(position):
                gradientBrush.setColorAt(0, darkColor)
                gradientBrush.setColorAt(1, brightColor)
            else:
                gradientBrush.setColorAt(0, brightColor)
                gradientBrush.setColorAt(1, darkColor)
            item.setBackground(gradientBrush)

    def isUpperHalfInItem(self, position):
        """マウスカーソルが現在の要素の半分より上にあるかどうかを返す。
        :param position: QPoint
        :return: bool
        
        rect.center().y()は、要素を規準にした位置ではなくListWidgetでのpostionを返すので、
        position.y()で比較できる。
        """
        rect = self.visualItemRect(self.itemAt(position))
        return position.y() < rect.center().y()

    def changeItemBackground(self, index, color=QColor(255,255,255)):
        """indexの背景色を変える。デフォルトでは、白にする。
        :param index: QAbstractIndexItem
        :param color: QColor
        :return: nothing
        """
        item = self.itemFromIndex(index)
        if item:
            item.setBackground(QBrush(color))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    playlist.debugUI()
    sys.exit(app.exec_())