import unittest
import sys
from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout

from playlist import Playlist

app = QApplication(sys.argv)

class TestPlaylist(unittest.TestCase):

    def setUp(self):
        self.playlist = Playlist()

    def test_playlists(self):
        self.assertEqual(self.playlist.playlist_tab.count(), 1)
        self.assertEqual(self.playlist.playlist_tab.add_playlist(), True)
        self.assertEqual(self.playlist.playlist_tab.count(), 2)
        self.playlist.playlist_tab.add_playlist()
        count = self.playlist.playlist_tab.count()
        self.playlist.playlist_tab.remove_playlist()
        self.assertEqual(self.playlist.playlist_tab.count(), count-1)

if __name__ == '__main__':
    #
    # file_url = []
    # current_dir = QDir.current()
    # for file in current_dir.entryList():
    #     if file == '.' or file == '..':
    #         continue
    #     file_url.append(QUrl('{0}/{1}'.format(current_dir.absolutePath(), file)))
    # playlist.playlist_tab.currentWidget().add_items(file_url)

    unittest.main()
