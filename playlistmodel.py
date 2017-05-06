from PyQt5.QtCore import QAbstractListModel, QUrl, QModelIndex, QVariant, Qt


class PlaylistModel(QAbstractListModel):

    def __init__(self, parent: object = None) -> object:
        super(PlaylistModel, self).__init__(parent)

        self.url_list = []
        self.headerTitles = ['Title', 'Duration']

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return a number of length of urls

        :type parent: QModelIndex
        :return int
        """
        return len(self.url_list)

    def data(self, index: QModelIndex, role: int = None) -> QVariant:
        if not index.isValid():
            return QVariant()

        if index.row() >= self.rowCount():
            return QVariant()

        if role == Qt.DisplayRole:
            return QVariant(self.url_list[index.row()].fileName())
        elif role == Qt.ToolTip or role is None:
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

    def add_url(self, url: QUrl, position: int = -1) -> bool:
        if not url.isValid():
            return False

        self.beginInsertRows(QModelIndex(), position, position)

        if position >= self.rowCount() or position < 0:
            self.url_list.append(url)
        else:
            self.url_list.insert(position, url)

        self.endInsertRows()
        return True

