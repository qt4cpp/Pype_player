import os
import unittest
import sys
from PyQt5.QtWidgets import QApplication

from playlist import Playlist

app = QApplication(sys.argv)

class TestPlaylist(unittest.TestCase):

    def setUp(self):
        self.playlist = Playlist()
        self.save_path = 'test_playlist/'
        self.extension = '.m3u8'

    def test_playlists(self):
        self.assertEqual(self.playlist.widget.count(), 1)
        self.assertEqual(self.playlist.widget.add_playlist(), True)
        self.assertEqual(self.playlist.widget.count(), 2)

        self.playlist.widget.add_playlist()
        count = self.playlist.widget.count()
        self.playlist.widget.setCurrentIndex(count - 1)
        self.playlist.widget.remove_playlist()
        self.assertEqual(self.playlist.widget.count(), count - 1)

    def test_save_remove(self):
        self.playlist.widget.add_playlist()
        self.assertEqual(self.playlist.widget.count(), 2)
        title = self.playlist.widget.tabText(1)
        self.playlist.widget.save_all()
        file_list = os.listdir(self.save_path)
        self.assertEqual(title+self.extension, file_list[0])
        self.remove_saved_files()

    def remove_saved_files(self):
        import shutil
        shutil.rmtree(self.save_path)

if __name__ == '__main__':
    unittest.main()
