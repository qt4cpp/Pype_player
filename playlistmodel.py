from operator import index

from PyQt5.QtCore import QAbstractListModel, QUrl, QModelIndex, QVariant, Qt


class PlaylistModel(QAbstractListModel):

    def __init__(self, parent: object = None):
        """

        :rtype: PlaylistModel
        """
        super(PlaylistModel, self).__init__(parent)

        self.url_list = []
        self.headerTitles = ['Title', 'Duration']

    def rowCount(self, parent: QModelIndex = QModelIndex(), **kwargs) -> int:
        """Return a number of length of urls

        :param **kwargs: 
        :type parent: QModelIndex
        :return int
        """
        return len(self.url_list)

    def data(self, index: QModelIndex, role: int = None) -> QVariant:
        """引数のindexの値をroleにあった形で返す。

        :param index: QModeIndex
        :param role: int
        :return: QVariant
        """
        if not index.isValid():
            return QVariant()

        if index.row() >= self.rowCount():
            return QVariant()

        if role == Qt.DisplayRole:
            return self.url_list[index.row()].fileName()
        elif role == Qt.ToolTipRole or role is None:
            return self.url_list[index.row()]
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

    def flags(self, index : QModelIndex):
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

        self.endInsertRows()
        return True

    def remove(self, position: int = -1) -> bool:
        if position >= self.rowCount():
            return False
        elif position == -1:
            position = self.rowCount() - 1

        self.beginRemoveRows(QModelIndex(), position, 1)
        del(self.url_list[position])
        self.endRemoveRows()
        return True

    def move(self, indexes : [QModelIndex], destination=-1) -> bool:
        #TODO: 大きいindexから消去する。
        max_index = max(indexes)
        min_index = min(indexes)

        begin = max_index.row()
        end = min_index.row()
        if destination < 0:
            destination = self.rowCount()
        if end <= destination <= begin+1:
            return False

        self.beginMoveRows(QModelIndex(), begin, end, QModelIndex(), destination)

        move_list = []
        delete_index = []
        for index in indexes:
            move_list.append(self.url_list[index.row()])
            delete_index.append(index.row())
        delete_index.sort(reverse=True)
        for index in delete_index:
            self.remove(index)
        if destination > begin:
            dest = destination - len(move_list)
        else:
            dest = destination
        self.url_list[dest:dest] = move_list

        self.endMoveRows()
        return True
