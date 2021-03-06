import unittest
from playlistmodel import PlaylistModel
from PyQt5.QtCore import QModelIndex, QVariant, Qt, QDir, QUrl


class TestPlaylistModel(unittest.TestCase):

    def setUp(self):
        self.playListModel = PlaylistModel()

    def test_rowCount(self):
        self.assertEqual(self.playListModel.rowCount(), 0)

    def test_data(self):
        self.assertEqual(self.playListModel.data(QModelIndex(), None), QVariant())

    def test_headerData(self):
        header_data = self.playListModel.headerData
        self.assertEqual(header_data(0, Qt.Horizontal), QVariant())
        self.assertEqual(header_data(0, Qt.Horizontal, Qt.DisplayRole), 'Title')
        self.assertEqual(header_data(1, Qt.Horizontal, Qt.DisplayRole), 'Duration')

        self.assertEqual(header_data(0, Qt.Vertical), QVariant())
        self.assertEqual(header_data(0, Qt.Vertical, Qt.DisplayRole), '1.')
        self.assertEqual(header_data(100, Qt.Vertical, Qt.DisplayRole), '101.')

    def test_add(self):
        model: PlaylistModel = self.playListModel

        invalid_url = QUrl('file:/!!//a;''|]~``/b/c/???_rewoui.xf!!', QUrl.StrictMode)
        self.assertEqual(model.add(invalid_url), False)

        current_dir = QDir.current_url()
        first_file = current_dir.entryList()[2]  # first = ., second = ..
        first_file_url = QUrl('{0}/{1}'.format(current_dir.absolutePath(), first_file))
        self.assertEqual(model.add(first_file_url), True)
        self.assertEqual(model.rowCount(), 1)

        index = model.index(0, 0)
        data = model.data(index, None)
        self.assertEqual(data, first_file_url)
        print(model.item_list[0].url)

    def test_del(self):
        model: PlaylistModel = self.playListModel

        current_dir = QDir.current_url()
        for file in current_dir.entryList():
            file_url = QUrl('{0}/{1}'.format(current_dir.absolutePath(), file))
            model.add(file_url)

        self.assertEqual(model.remove(0), True)
        self.assertEqual(model.remove(1), True)
        self.assertEqual(model.remove(model.rowCount()), False)
        print(model.item_list[0])


if __name__ == '__main__':
    unittest.main()
