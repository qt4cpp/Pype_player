from PySide2.QtCore import QUrl, QModelIndex, Qt, Signal, Slot, QAbstractTableModel, QTime
from PySide2.QtGui import QFont, QBrush, QColor

from pymediainfo import MediaInfo


class PlaylistModel(QAbstractTableModel):

    rowCount_changed = Signal(int)
    set_current_index = Slot(QModelIndex)

    def __init__(self, parent: object = None):
        """

        :rtype: PlaylistModel
        """
        super(PlaylistModel, self).__init__(parent)

        self.item_list = []
        self.headerTitles = ['Title', 'Duration']
        self.current_index = QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex(), **kwargs) -> int:
        """Return a number of length of urls

        :param **kwargs: 
        :type parent: QModelIndex
        :return int
        """
        return len(self.item_list)

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def data(self, index: QModelIndex, role: int = None):
        """引数のindexの値をroleにあった形で返す。

        :param index: QModeIndex
        :param role: int
        :return: QVariant
        """
        row = index.row()
        col = index.column()
        if not index.isValid():
            return None

        if row >= self.rowCount():
            return None
        if role == Qt.DisplayRole:
            if col == 0:
                return self.item_list[row]['url'].fileName()
            elif col == 1:
                return self.item_list[row]['duration']
        elif role == Qt.TextAlignmentRole:
            if col == 1:
                return Qt.AlignRight | Qt.AlignVCenter
        elif role == Qt.FontRole:
            font = QFont()
            if row == self.current_index.row():
                font.setBold(True)
            font.setPointSize(11)
            return font
        elif role == Qt.BackgroundRole:
            if row == self.current_index.row():
                brush = QBrush(QColor(210, 230, 250))
                return brush

        elif role == Qt.ToolTipRole or role is None:
            return self.item_list[row]['url']
        else:
            return 0

    def headerData(self, section: int, orientation, role: int =None):
        """

        :param role: Qt.DisplayRole
        :param orientation: Qt.Orientation
        :type section: int
        
        """
        if role != Qt.DisplayRole:
            return 0

        if orientation == Qt.Horizontal:
            return self.headerTitles[section]
        else:
            return '{0}.'.format(section+1)

    def flags(self, index: QModelIndex):
        """

        :type index: QModelIndex
        """
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def add(self, url: QUrl, position: int = -1) -> bool:

        if not url.isValid():
            return False

        media_info = MediaInfo.parse(url.toLocalFile())
        for track in media_info.tracks:
            if track.duration is None:
                duration_str = '--:--'
            else:
                duration = float(track.duration) / 1000
                totalTime = QTime((duration / 3600) % 60, (duration / 60) % 60, (duration % 60),
                                  (duration * 1000) % 1000)

                format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
                duration_str = totalTime.toString(format)

        if position >= self.rowCount() or position < 0:
            position = self.rowCount()

        self.beginInsertRows(QModelIndex(), position, position+1)

        media_info = {'url': url, 'duration': duration_str}
        self.item_list.insert(position, media_info)

        self.endInsertRows()
        self.rowCount_changed.emit(self.rowCount())
        return True

    def remove(self, position: int = -1) -> bool:
        if position >= self.rowCount():
            return False
        elif position == -1:
            position = self.rowCount() - 1

        self.beginRemoveRows(QModelIndex(), position, position+1)
        del(self.item_list[position])
        self.endRemoveRows()
        self.rowCount_changed.emit(self.rowCount())
        return True

    def remove_items(self, indexes: [QModelIndex]):
        rows = []
        for index in indexes:
            rows.append(index.row())
        for row in reversed(list(set(rows))):
            self.remove(row)

    def move(self, indexes: [QModelIndex], dest=-1) -> bool:
        """要素を指定された場所へ移動させる。
        
        :param indexes: 移動させる要素を指すインデックスのリスト
        :param dest: 移動させる先
        :return: 成功すればTrue, それ以外はFalse
        要素を消してから移動させる。消すときインデックスが変わってしまうので、大きいインデックスから消していく。
        """
        if indexes[0].row() < indexes[-1].row():
            min_index_row = indexes[0].row()
            max_index_row = indexes[-1].row()
        else:
            min_index_row = indexes[-1].row()
            max_index_row = indexes[0].row()
        if dest < 0:
            dest = self.rowCount()
        elif min_index_row <= dest <= max_index_row+1:  # 移動先のindex が選択内なら終了する
            return False

        begin = min_index_row
        end = max_index_row
        self.beginMoveRows(QModelIndex(), begin, end, QModelIndex(), dest)
        if dest < begin:
            for i in range(begin, end+1):
                self.item_list.insert(dest, self.item_list.pop(end))
        elif dest > end+1:
            for i in range(begin, end+1):
                self.item_list.insert(dest-1, self.item_list.pop(begin))
        self.endMoveRows()
        self.rowCount_changed.emit(self.rowCount())
        return True

    def set_current_index(self, index: QModelIndex):
        self.current_index = index
