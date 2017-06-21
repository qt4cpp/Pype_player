from PyQt5.QtCore import QModelIndex, QRect, QSize, QPoint, pyqtSignal, QDir, Qt, QMimeData, QUrl, \
    QByteArray, QTextStream, QIODevice, pyqtSlot, QFile
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QListView, QRubberBand, QFileDialog, QAbstractItemView, QApplication, \
    QStyle, QInputDialog

from playlistmodel import PlaylistModel
from utility import convert_from_bytearray, convert_to_bytearray


class PlaylistView(QListView):

    current_index_changed = pyqtSignal(QModelIndex)
    playlist_double_clicked = pyqtSignal()
    next = pyqtSlot(int)
    previous = pyqtSlot(int)

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
    @property
    def open_file_filter(self):
        return '*.mp4 *.m4v *.mov *.mpg *.mpeg *.mp3 *.m4a *.wmv'
    @property
    def current_row(self):
        return self.current_index.row()

    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        self.setModel(PlaylistModel())

        self.current_index = QModelIndex()
        self.previousIndex = QModelIndex()
        self.rubberBand: QRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.isDragging = False

        self.current_index_changed.connect(self.model().set_current_index)

    def count(self):
        return self.model().rowCount()

    def open(self):
        file_urls, _ = QFileDialog.getOpenFileUrls(
            self, 'Open File', QDir.homePath(), self.open_file_filter)

        for url in file_urls:
            if not url.isEmpty():
                self.model().add(url)

    def save(self, name=None, use_dialog=False):
        """プレイリストを保存する。

        :param file :QFile 出力するようのファイル
        fileが指定されていれば、fileに内容を書き込み、
        指定がなければ、ダイアログで名前を指定してそこにファイルを保存。
        """
        import os.path

        if name is None:
            name = 'untitled'

        if use_dialog:
            url, ok = QFileDialog.getSaveFileUrl(self, 'Save File', name+'.m3u', 'playlist(*.m3u')
            if not ok:
                return False
            url = url.toLocalFile()
        else:
            if not os.path.exists('playlist'):
                os.mkdir('playlist')
            url = 'playlist/' + name + '.m3u'

        with open(url, 'wt') as fout:
            for i in range(self.model().rowCount()):
                index = self.model().index(i)
                print(self.model().data(index).toString(), file=fout)
        return True

    def current(self):
        selected_url = self.selected()
        if selected_url is not None:
            self.set_current_index(selected_url)
        elif not self.current_index.isValid():
            self.set_current_index_from_row(0)
        return self.url(self.current_index)

    def next(self, step=1):
        self.set_current_index_from_row(self.current_index.row() + step)
        return self.url(self.current_index)

    def previous(self, step=1):
        self.set_current_index_from_row(self.current_index.row() - step)
        return self.url(self.current_index)

    def selected(self):
        selected_indexes = self.selectedIndexes()
        if len(selected_indexes) > 0:
            return selected_indexes[0]
        else:
            return None

    def url(self, index):
        if isinstance(index, int):
            row = index
            if 0 <= row < self.count():
                index = self.model().index(row)
        if isinstance(index, QModelIndex):
            return self.model().data(index)
        else:
            return None

    def set_current_index_from_row(self, row):
        new_index = self.model().index(row)
        return self.set_current_index(new_index)

    def set_current_index(self, new_index: QModelIndex):
        self.current_index = new_index
        self.current_index_changed.emit(self.current_index)

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
            urls = self.pack_urls(indexes)

            mimeData = QMimeData()
            mimeData.setData(self.mime_URLS, convert_to_bytearray(urls))

            file_icon = self.style().standardIcon(QStyle.SP_FileIcon)
            pixmap = file_icon.pixmap(32, 32)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(0, 0))

            dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
            if dropAction == Qt.MoveAction:
                pass

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

        if event.mimeData().hasUrls() or event.mimeData().hasFormat(self.mime_URLS):
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
        if event.mimeData().hasUrls() or event.mimeData().hasFormat(self.mime_URLS):
            self.rubberBand.setGeometry(
                self.rectForDropIndicator(self.index_for_dropping_pos(event.pos())))
            self.rubberBand.show()
            self.previousIndex = self.indexAt(event.pos())
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()


    def dragLeaveEvent(self, event):
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
        if event.mimeData().hasUrls() or event.mimeData().hasFormat(self.mime_URLS):
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
            else:
                urls = convert_from_bytearray(event.mimeData().data(self.mime_URLS))
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


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            new_index = self.indexAt(event.pos())
            self.set_current_index(new_index)
            self.playlist_double_clicked.emit()


    def add_items(self, items: [QUrl], start: int = -1):
        """渡された要素をmodelに追加する。

        :param items: 追加する項目
        :param start: 追加するindexを表す。初期値は-1
        start に −1を渡すと一番後ろに追加する。
        """
        if isinstance(items, QUrl):
            self.model().add(items)
        elif start == -1:
            for item in items:
                self.model().add(item)
        else:
            for item, i in items, range(start, len(items)):
                self.model().add(item, i)


    def delete_items(self, indexes: [QModelIndex]):
        """渡されたインデックスを順番に消していく。

        :param indexes: 消すためのインデックス
        """
        for index in indexes:
            self.model().remove(index.row())


    def move_items(self, indexes: [QModelIndex], dest: QModelIndex):
        self.model().move(indexes, dest.row())


    def index_for_dropping_pos(self, pos: QPoint) -> QModelIndex:
        """dropした場所のindexを返す。ただし、要素の高さ半分より下にある場合は、下の要素を返す。

        :param pos:
        :return: posから導き出されたindex
        挿入や移動のために、要素の間を意識している。
        """
        index = self.indexAt(pos)
        if index.row() < 0:
            new_index = self.model().index(self.model().rowCount(), 0)
            return new_index

        item_rect = self.visualRect(index)
        pos_in_rect = pos.y() - item_rect.top()
        if pos_in_rect < (item_rect.height() / 2):
            return index
        else:
            return self.model().index(index.row() + 1, 0)


    def rectForDropIndicator(self, index: QModelIndex) -> QRect:
        """QRubberBand を DropIndicatorとして表示するためのQRectを返す。
        Geometryに渡されるので、表示位置となるようにQRectを作成する。
        幅が表示領域、縦1pixelの棒で表示する。
        """
        item_rect = self.visualRect(index)
        top_left = item_rect.topLeft()
        size = QSize(item_rect.width(), 3)
        return QRect(top_left, size)
