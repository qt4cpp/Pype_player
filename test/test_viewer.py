import unittest
import sys
from PyQt5.QtWidgets import QApplication

from viewer import Viewer

app = QApplication(sys.argv)

class TestViewer(unittest.TestCase):

    def setUp(self):
        self.viewer = Viewer()
        self.image_path = 'image/duo-270.png'

    def test_load_image(self):
        pixmap = self.viewer.image_viewer.load_image(self.image_path)
        self.assertNotEqual(pixmap, False)
        self.viewer.resize(400, 400*self.viewer.image_viewer.aspect_ratio())
        self.assertEqual(min(self.viewer.width(), self.viewer.height()), 400)

    def test_add_set(self):
        self.viewer.add_item(self.image_path)
        self.viewer.set_image(0)
        self.viewer.set_image(-2)

    def test_next_previous(self):
        self.viewer.open_directory('image/')
        self.assertNotEqual(len(self.viewer.image_list), 0)
        self.viewer.set_image(0)
        self.viewer.next()
        self.viewer.previous()
        self.assertEqual(self.viewer.index, 0)


if __name__ == '__main__':
    unittest.main()