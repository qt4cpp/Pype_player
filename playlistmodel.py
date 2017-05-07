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
        if not index.isValid():
            return QVariant()

        if index.row() >= self.rowCount():
            return QVariant()

        if role == Qt.DisplayRole or role is None:
            return self.url_list[index.row()].fileName()
        elif role == Qt.ToolTipRole or role is None:
            return QVariant(self.url_list[index.row()])
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
        if not index.isValid():
            return 0

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def add_url(self, url: QUrl, position: int = -1) -> bool:
        if not url.isValid():
            return False

        if position >= self.rowCount() or position < 0:
            position = self.rowCount()

        self.beginInsertRows(QModelIndex(), position, 1)

        self.url_list.insert(position, url)

        self.endInsertRows()
        return True
