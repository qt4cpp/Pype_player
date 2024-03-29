from PySide2.QtCore import QModelIndex, QRect, QSize, QPoint, Signal, QDir, \
    Qt, QMimeData, QUrl, Slot, QSortFilterProxyModel, QRegularExpression
from PySide2.QtWidgets import QRubberBand, QFileDialog, QAbstractItemView,\
    QApplication, QStyle, QTableView, QHeaderView, QMenu
from PySide2.QtGui import QDrag

from playlistmodel import PlaylistModel
from utility import convert_from_bytearray, is_media, createAction

class PlaylistView(QTableView):

    current_index_changed = Signal(QModelIndex)
    playlist_double_clicked = Signal()
    filtering = Signal(str)
    unfiltered = Signal(str)
    next = Slot(int)
    previous = Slot(int)

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
        return '*.mp4 *.m4v *.mov *.mpg *.mpeg *. mp3 *.m4a *.wmv *.aiff *.wav'

    def __init__(self, parent=None):
        super(PlaylistView, self).__init__(parent)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(PlaylistModel(self))
        self.setModel(self.proxy_model)
        # self.setModel(PlaylistModel())

        self.setShowGrid(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setDefaultSectionSize(16)
        self.verticalHeader().hide()
        self.horizontalHeader().setMinimumSectionSize(30)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self.current_index = QModelIndex()
        self.previousIndex = QModelIndex()
        self.rubberBand: QRubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.isDragging = False
        self.wasSelected = False

        self.context_menu = QMenu(self)
        self.create_context_menu()

        # self.current_index_changed.connect(self.proxy_model.sourceModel().set_current_index)
        self.current_index_changed.connect(self.proxy_model.sourceModel().set_current_index)

    def create_context_menu(self):
        add_file = createAction(self, 'Add File(s)', self.open)
        delete_selected = createAction(self, 'Delete selected', self.delete_items)
        sort_action = createAction(self, 'Sort', self.proxy_model.sourceModel().sort)
        pickup_dup_action = createAction(self, 'Filter by same title', self.filter_same_title)
        stop_filtering_action = createAction(self, 'Stop Filtering', self.unfilter)
        self.context_menu.addActions([add_file, delete_selected, sort_action, pickup_dup_action, stop_filtering_action])

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def count(self):
        return self.proxy_model.sourceModel().rowCount()

    def open(self):
        list, _ = QFileDialog.getOpenFileNames(
            self, 'Open File', QDir.homePath())

        for path in list:
            if path[-3:] == 'm3u':
                self.load(path)
            else:
                self.add_item(path)

    def open_directory(self):
        directory_url = QFileDialog.getExistingDirectory(
            self, '0Open directory', QDir.homePath())
        dir = QDir(directory_url)
        filters = ['*.mp4', '*.m4v', '*.mov', '*.mpg', '*.mpeg', '*.mp3',
                   '*.m4a', '*.wmv', '*.wav', '*.aiff']
        dir.setNameFilters(filters)
        file_list = dir.entryList()

        path = dir.absolutePath() + '/'
        for file in file_list:
            self.add_item(path + file)

    def save(self, path=None):
        """プレイリストを保存する。

        :param file :QFile 出力するようのファイル
        fileが指定されていれば、fileに内容を書き込み、
        指定がなければ、ダイアログで名前を指定してそこにファイルを保存。
        """
        if path is None:
            return

        with open(path, 'wt') as fout:
            for i in range(self.proxy_model.sourceModel().rowCount()):
                index = self.proxy_model.sourceModel().index(i, 0)
                print(self.url(index).toLocalFile(), file=fout)
        return True

    def load(self, path=None):
        """プレイリストを読み込む

        pathが与えられた場合は、そこから読み込み、
        ない場合は、何も読み込まない。"""

        with open(path, 'rt') as fin:
            for line in fin:
                self.add_item(line[:-1])  # 最後の改行文字を取り除く

    def add_item(self, path):
        if is_media(path):
            self.proxy_model.sourceModel().add(QUrl.fromLocalFile(path))
            return True
        return False

    def current_url(self):
        return self.url(self.current_index)

    def current_title(self):
        return self.title(self.current_index)

    def next(self, step=1):
        if self.current_row() + step < self.count():
            self.set_current_index_from_row(self.current_row() + step)
            return self.url(self.current_index)
        else:
            return None

    def previous(self, step=1):
        if self.current_row() - step >= 0:
            self.set_current_index_from_row(self.current_row() - step)
            return self.url(self.current_index)
        else:
            return None

    def selected(self):
        selected_indexes = self.selectedIndexes()
        if len(selected_indexes) > 0:
            return selected_indexes[0]
        else:
            return None

    def current_row(self):
        return self.current_index.row()

    def url(self, index):
        if isinstance(index, int):
            row = index
            if 0 <= row < self.count():
                index = self.proxy_model.sourceModel().index(row, 0)
        if isinstance(index, QModelIndex):
            return self.proxy_model.sourceModel().data(index)
        else:
            return None

    def title(self, index):
        if isinstance(index, int):
            row = index
            if 0 <= row < self.count():
                index = self.proxy_model.sourceModel().index(row, 0)
        if isinstance(index, QModelIndex):
            return self.proxy_model.sourceModel().data(index, Qt.DisplayRole)
        else:
            return None

    def set_current_index_from_row(self, row):
        new_index = self.proxy_model.sourceModel().index(row, 0)
        return self.set_current_index(new_index)

    def set_current_index(self, new_index: QModelIndex):
        self.current_index = new_index
        self.current_index_changed.emit(new_index)

    def deactivate(self):
        self.set_current_index(QModelIndex())

    def auto_resize_header(self):
        """auto resize Header width on table view.
        """
        width = self.viewport().width()
        duration_width = 120
        self.horizontalHeader().resizeSection(0, width - duration_width)
        self.horizontalHeader().resizeSection(1, duration_width)

    def mousePressEvent(self, event):
        """左クリックされたらカーソル下にある要素を選択し、ドラッグを認識するために現在の位置を保存する。
        :param event: QMousePressEvent
        :return: nothing
        """
        self.isDragging = False
        if Qt.LeftButton == event.button():
            self.dragStartPosition = event.pos()

            index = self.indexAt(self.dragStartPosition)
            if index in self.selectedIndexes():
                self.isDragging = True
                self.wasSelected = True
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
            urls = self.url_list(indexes)

            mimeData = QMimeData()
            # mimeData.setData(self.mime_URLS, convert_to_bytearray(urls))
            mimeData.setUrls(urls)

            file_icon = self.style().standardIcon(QStyle.SP_FileIcon)
            pixmap = file_icon.pixmap(32, 32)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(0, 0))

            dropAction = drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction)
            if dropAction == Qt.MoveAction:
                pass

        else:
            self.rubberBand.setGeometry(QRect(self.dragStartPosition, event.pos()).normalized())
            super(PlaylistView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        '''マウスを離したときにQRubberBandを隠す。
        左クリックをpress と release がだいたい同じ位置であれば、その要素を1つだけ選択する。

        :param event:
        '''
        self.rubberBand.hide()
        if Qt.LeftButton == event.button() and Qt.NoModifier == event.modifiers():
            if self.indexAt(event.pos()).row() == -1 and \
               self.indexAt(self.dragStartPosition).row() == -1:
                self.clearSelection()
            elif len(self.selectedIndexes())/2 == 1 and self.wasSelected == True:
                self.clearSelection()
            elif (event.pos() - self.dragStartPosition).manhattanLength() \
                 < QApplication.startDragDistance():
                self.setCurrentIndex(self.indexAt(event.pos()))
        self.wasSelected = False
        super(PlaylistView, self).mouseReleaseEvent(event)

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
            if not new_index.isValid():
                return
            self.selectRow(new_index.row())
            self.playlist_double_clicked.emit()

    def add_items(self, items: [QUrl], start: int = -1):
        """渡された要素をmodelに追加する。

        :param items: 追加する項目
        :param start: 追加するindexを表す。初期値は-1
        start に −1を渡すと一番後ろに追加する。
        """
        if isinstance(items, QUrl):
            self.proxy_model.sourceModel().add(items)
        elif start == -1:
            for item in items:
                self.proxy_model.sourceModel().add(item)
        else:
            for item, i in items, range(start, len(items)):
                self.proxy_model.sourceModel().add(item, i)

    def delete_items(self):
        """渡されたインデックスを順番に消していく。

        :param indexes: 消すためのインデックス
        """
        indexes = self.selectedIndexes()
        if indexes:
            self.proxy_model.sourceModel().remove_items(indexes)
        else:
            return

    def move_items(self, indexes: [QModelIndex], dest: QModelIndex):
        self.proxy_model.sourceModel().move(indexes, dest.row())

    def filter_same_title(self):
        dup = self.proxy_model.sourceModel().pickup_same_title()
        re = QRegularExpression('|'.join(dup))
        self.proxy_model.setFilterRegularExpression(re)
        self.filtering.emit(' - filtered')

    def unfilter(self):
        self.proxy_model.setFilterWildcard('*')
        self.unfiltered.emit('')

    def index_for_dropping_pos(self, pos: QPoint) -> QModelIndex:
        """dropした場所のindexを返す。ただし、要素の高さ半分より下にある場合は、下の要素を返す。

        :param pos:
        :return: posから導き出されたindex
        挿入や移動のために、要素の間を意識している。
        """
        index = self.indexAt(pos)
        if index.row() < 0:
            new_index = self.proxy_model.sourceModel().index(self.proxy_model.sourceModel().rowCount(), 0)
            return new_index

        item_rect = self.visualRect(index)
        pos_in_rect = pos.y() - item_rect.top()
        if pos_in_rect < (item_rect.height() / 2):
            return index
        else:
            return self.proxy_model.sourceModel().index(index.row() + 1, 0)

    def rectForDropIndicator(self, index: QModelIndex) -> QRect:
        """QRubberBand を DropIndicatorとして表示するためのQRectを返す。
        Geometryに渡されるので、表示位置となるようにQRectを作成する。
        幅が表示領域、縦1pixelの棒で表示する。
        """
        item_rect = self.visualRect(index)
        top_left = item_rect.topLeft()
        size = QSize(item_rect.width(), 3)
        return QRect(top_left, size)

    def url_list(self, indexes):
        urls = []
        for index in indexes:
            urls.append(self.proxy_model.sourceModel().data(index))
        return sorted(set(urls), key=urls.index)
