import os
import unittest
import sys
from PyQt5.QtWidgets import QApplication

from playlist import Playlist

app = QApplication(sys.argv)

class TestPlaylist(unittest.TestCase):

    def setUp(self):
        self.playlist = Playlist()
        self.save_path = 'playlist/'

    def test_playlists(self):
        self.assertEqual(self.playlist.playlist_tab.count(), 1)
        self.assertEqual(self.playlist.playlist_tab.add_playlist(), True)
        self.assertEqual(self.playlist.playlist_tab.count(), 2)

        self.playlist.playlist_tab.add_playlist()
        count = self.playlist.playlist_tab.count()
        self.playlist.playlist_tab.setCurrentIndex(count-1)
        self.playlist.playlist_tab.remove_playlist()
        self.assertEqual(self.playlist.playlist_tab.count(), count-1)

    def test_save_remove(self):
        self.playlist.playlist_tab.add_playlist()
        self.assertEqual(self.playlist.playlist_tab.count(), 2)
        title = self.playlist.playlist_tab.tabText(1)
        self.playlist.playlist_tab.save_all()
        file_list = os.listdir(self.save_path)
        self.assertEqual(title+'.m3u', file_list[0])
        self.remove_saved_files()

    def remove_saved_files(self):
        import shutil
        shutil.rmtree(self.save_path)

if __name__ == '__main__':
    unittest.main()
