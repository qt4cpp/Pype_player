from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel


class ImageViewer(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.factor = 1.0
        self.setScaledContents(True)

    def set_image(self, path='', ):
        # check file exists
        pixmap = QPixmap()
        pixmap.load(path)
        # check null
        self.setPixmap(pixmap)
        return pixmap

    def scale_image(self, factor):
        self.factor *= factor
        self.resize(self.factor * self.pixmap().size())

    def resize_keep_aspect_ratio(self, base_size=500):
        height = self.pixmap().height()
        width = self.pixmap().width()
        if height > width:
            self.resize(base_size, base_size*self.aspect_ratio())
        else:
            self.resize(base_size*self.aspect_ratio(), base_size)

    def aspect_fit(self, size: QSize):
        if self.pixmap().width() > self.pixmap().height():
            self.scale_image(size.width() / self.width())
        else:
            self.scale_image(size.height() / self.height())
            print(self.factor)

    def aspect_ratio(self):
        width = self.pixmap().width()
        height = self.pixmap().height()
        return max(width, height) / min(width, height)

