from PyQt5.QtCore import QUrl, QModelIndex, QVariant, Qt, pyqtSignal, pyqtSlot, QAbstractTableModel
from PyQt5.QtGui import QFont

from pymediainfo import MediaInfo


class PlaylistModel(QAbstractTableModel):

    rowCount_changed = pyqtSignal(int)
    set_current_index = pyqtSlot(QModelIndex)

    def __init__(self, parent: object = None):
        """

        :rtype: PlaylistModel
        """
        super(PlaylistModel, self).__init__(parent)

        self.url_list = []
        self.duration = []
        self.headerTitles = ['Title', 'Duration']
        self.current_index = QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex(), **kwargs) -> int:
        """Return a number of length of urls

        :param **kwargs: 
        :type parent: QModelIndex
        :return int
        """
        return len(self.url_list)

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
        elif col == 1:
            return
        if role == Qt.DisplayRole:
            return self.url_list[row].fileName()
        elif role == Qt.FontRole and row == self.current_index.row():
            bold_font = QFont()
            bold_font.setBold(True)
            return bold_font
        elif role == Qt.ToolTipRole or role is None:
            return self.url_list[row]
        else:
            return QVariant()

    def headerData(self, section: int, orientation, role: int =None):
        """

        :param role: Qt.DisplayRole
        :param orientation: Qt.Orientation
        :type section: int
        
        """
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return self.headerTitles[section]
        else:
            return '{0}.'.format(section+1)

    def flags(self, index: QModelIndex):
        """

        :type index: QModelIndex
        """
        if not index.isValid():
            return 0

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def add(self, url: QUrl, position: int = -1) -> bool:
        if not url.isValid():
            return False

        if position >= self.rowCount() or position < 0:
            position = self.rowCount()

        self.beginInsertRows(QModelIndex(), position, 1)

        self.url_list.insert(position, url)

        media_info = MediaInfo.parse(url.toLocalFile())
        for track in media_info.tracks:
            if track.track_type == 'Audio' or track.track_type == 'Video':
                duration = track.duration / 1000
                print(duration)
                print('{0} | {1:.0f}:{2:.0f}'.format(track.Title, duration/60, duration%60))

        self.endInsertRows()
        self.rowCount_changed.emit(self.rowCount())
        return True

    def remove(self, position: int = -1) -> bool:
        if position >= self.rowCount():
            return False
        elif position == -1:
            position = self.rowCount() - 1

        self.beginRemoveRows(QModelIndex(), position, 1)
        del(self.url_list[position])
        self.endRemoveRows()
        self.rowCount_changed.emit(self.rowCount())
        return True

    def move(self, indexes: [QModelIndex], dest=-1) -> bool:
        """要素を指定された場所へ移動させる。
        
        :param indexes: 移動させる要素を指すインデックスのリスト
        :param dest: 移動させる先
        :return: 成功すればTrue, それ以外はFalse
        要素を消してから移動させる。消すときインデックスが変わってしまうので、大きいインデックスから消していく。
        """
        max_index = max(indexes)
        min_index = min(indexes)
        if dest < 0:
            dest = self.rowCount()
        elif min_index.row() <= dest <= max_index.row()+1:
            return False

        begin = max_index.row()
        end = min_index.row()
        self.beginMoveRows(QModelIndex(), begin, end, QModelIndex(), dest)
        move_list = []
        delete_index = []
        for index in indexes:
            move_list.append(self.url_list[index.row()])
            delete_index.insert(0, index.row())
        for index in delete_index:
            self.remove(index)

        dest = dest - len(move_list) if dest > begin else dest
        self.url_list[dest:dest] = move_list
        self.endMoveRows()
        self.rowCount_changed.emit(self.rowCount())
        return True

    def set_current_index(self, index: QModelIndex):
        if index.isValid():
            self.current_index = index
