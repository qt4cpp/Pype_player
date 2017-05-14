from PyQt5.QtCore import (QUrl, QMimeData, Qt, QDir, QModelIndex, QPoint, QRect, QSize, QByteArray,
                          QIODevice, QTextStream)
from PyQt5.QtGui import QDrag, QPixmap, QRegion, QBrush, QDragLeaveEvent
from PyQt5.QtWidgets import (QApplication, QFileDialog, QRubberBand,
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
            self.m_playlist.add(fileURL)

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
    def mime_URLS(self):
        return 'application/x-file-urls'
    @property
    def mime_url_count(self):
        return 'application/x-urls-count'
    @property
    def url_delimiter(self):
        return '\n'

    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)

        self.previousIndex = QModelIndex()
        self.originalBackground = QBrush()
        self.rubberBand: QRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.isDragging = False

    def mousePressEvent(self, event):
        """左クリックされたらカーソル下にある要素を選択し、ドラッグを認識するために現在の位置を保存する。
        :param event: QMousePressEvent
        :return: nothing
        """
        self.isDragging = False
        if Qt.LeftButton == event.button():
            self.dragStartPosition = event.pos()

            index = self.indexAt(self.dragStartPosition)
            if index.row() == -1:
                self.clearSelection()
            if index in self.selectedIndexes():
                self.isDragging = True
                return

            self.rubberBand.setGeometry(QRect(self.dragStartPosition, QSize()))
            self.rubberBand.show()

        super(PlaylistView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """start Drag and prepare for Drop.

        :type event: QMoveEvent
        マウスを動かした嶺がQApplication.startDragDistance()を超えると、Drag開始されたと認識し、
        そのための準備を行う。QMimeDataを使って、データをやりとりする。
        """
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() \
                < QApplication.startDragDistance():
            return

        if self.isDragging:
            indexes = self.selectedIndexes()
            urls = self.convert_to_bytearray(indexes)
            mimeData = QMimeData()
            mimeData.setText(str(len(indexes)))
            mimeData.setData(self.mime_URLS, urls)

            dragRect = self.rect_for_drag_items(indexes)
            pixmap = QPixmap(dragRect.width(), dragRect.height())
            renderSource = QRegion(dragRect)
            self.render(pixmap, sourceRegion=renderSource,)

            drag = QDrag(self)
            drag.setHotSpot(event.pos())
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)

            dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
            if dropAction == Qt.MoveAction:
                pass
                # self.delete_items(indexes)

        else:
            self.rubberBand.setGeometry(QRect(self.dragStartPosition, event.pos()).normalized())
            super(PlaylistView, self).mouseMoveEvent(event)

    def dragEnterEvent(self, event):
        """ドラッグした状態でWidgetに入った縁で呼ばれる関数。
        :param event: QDragEvent
        :return: nothing
        
        イベントが発生元と発生しているWidgetが同一の場合はMoveActionにする。それ以外はCopyAction。
        その二つの場合は受け入れられるように、accept()もしくはacceptProposedAction()を呼ぶ。
        """

        if event.mimeData().hasFormat(self.mime_URLS):
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
        if event.mimeData().hasFormat(self.mime_URLS):
            self.rubberBand.setGeometry(self.rectForDropIndicator(self.index_for_dropping_pos(event.pos())))
            self.rubberBand.show()
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
        self.rubberBand.hide()

    def mouseReleaseEvent(self, event):
        """マウスを離したときにQRubberBandを隠す。
        左クリックを押した位置と話した位置が同じであれば、その要素を選択する。

        :param event: 
        """
        self.rubberBand.hide()
        if Qt.LeftButton == event.button():
            if event.pos() == self.dragStartPosition:
                self.setCurrentIndex(self.indexAt(event.pos()))
        super(PlaylistView, self).mouseReleaseEvent(event)

    def dropEvent(self, event):
        """Dropされたらデータを取り出して、新たに登録する。
        :param event: QDropEvent
        :return: nothing
        
        ファイルへのパスと移動前に登録してあった要素のindexを取り出す。
        """
        self.rubberBand.hide()
        if event.mimeData().hasFormat(self.mime_URLS):
            data = event.mimeData().data(self.mime_URLS)
            urls = self.convert_from_bytearray(data)
            index = self.index_for_dropping_pos(event.pos())
            if event.source() is self:
                self.move_items(self.selectedIndexes(), index)
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                self.add_items(urls)
                event.acceptProposedAction()
        else:
            event.ignore()

    def add_items(self, items : [QUrl], start: int = -1):
        """渡された要素をmodelに追加する。

        :param items: 追加する項目
        :param start: 追加するindexを表す。初期値は-1
        start に −1を渡すと一番後ろに追加する。
        """
        if start == -1:
            for item in items:
                self.model().add(item)
        else:
            for item, position in items, range(len(items)):
                self.model().add(item, start + position)

    def delete_items(self, indexes : [QModelIndex]):
        """渡されたインデックスを十番に消していく。

        :param indexes: 消すためのインデックス
        """
        for index in indexes:
            self.model().remove(index.row())

    def move_items(self, indexes: [QModelIndex], dest : QModelIndex):
        self.model().move(indexes[0].row(), indexes[-1].row(), dest.row())

    def convert_to_bytearray(self, indexes : [QModelIndex]) -> QByteArray:
        """modelの項目をbyte型に変換する。

        :param indexes: 要素を変換するindexのリスト
        :return: byte型に変換した項目
        元に戻すための区切り文字としてself.url_delimiterプロパティを使用
        """
        urls_byte = QByteArray()
        stream = QTextStream(urls_byte, QIODevice.WriteOnly)
        for index in indexes:
            stream << self.model().data(index).toString() << self.url_delimiter

        return urls_byte

    def convert_from_bytearray(self, byte_array : QByteArray) -> [QUrl]:
        """渡されたbyte arrayから元のデータに復元する。

        :param byte_array: 
        :return: 
        区切り文字はself.url_delimiterプロパティ
        """
        byte_list = byte_array.split(self.url_delimiter)
        urls = []
        for data in byte_list:
            url = QUrl(data.data().decode('utf-8'))
            urls.append(url)
        return urls

    def rect_for_drag_items(self, indexes:[QModelIndex]) -> QRect:
        """dragされる要素を表す領域を返す。

        :param indexes: 
        :return: indexesが囲われているQRect
        """
        item_rect : QRect = self.rectForIndex(indexes[0])
        height = item_rect.height()
        width = item_rect.width()

        start_row = indexes[0].row()
        end_row = indexes[-1].row()

        top_left = QPoint(0, height*start_row)
        bottom_right = QPoint(width, height*(end_row+1))

        return QRect(top_left, bottom_right)

    def index_for_dropping_pos(self, pos : QPoint) -> QModelIndex:
        """dropした場所のindexを返す。ただし、要素の高さ半分より下にある場合は、下の要素を返す。

        :param pos: 
        :return: posから導き出されたindex
        挿入や移動のために、要素の間を意識している。
        """
        index = self.indexAt(pos)
        if index.row() < 0:
            new_index = self.model().index(self.model().rowCount(), 0)
            return new_index

        item_rect = self.rectForIndex(index)
        if (pos.y()%item_rect.height()) < (item_rect.height()/2):
            return index
        else:
            return self.model().index(index.row()+1, 0)

    def rectForDropIndicator(self, index : QModelIndex) -> QRect:
        """QRubberBand を DropIndicatorとして表示するためのQRectを返す。
        Geometryに渡されるので、表示位置となるようにQRectを作成する。
        幅が表示領域、縦1pixelの棒で表示する。
        """
        row = index.row()
        if row < 0:
            row = self.model().rowCount()
        print(row)
        item_rect = self.rectForIndex(self.model().index(0, 0))
        top_left = QPoint(0, item_rect.height()*row)
        size = QSize(item_rect.width(), 3)
        return QRect(top_left, size)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    playlist.debugUI()
    sys.exit(app.exec_())