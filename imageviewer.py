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
        self.adjustSize()
        return pixmap

    def scale_image(self, factor):
        if self.factor * factor > 4.76:
            self.factor = 4.76
        elif self.factor * factor < 0.1:
            self.factor = 0.1
        else:
            self.factor = round(factor * self.factor, 2)
        self.resize(self.factor * self.pixmap().size())
        print(self.factor)

    def resize_keep_aspect_ratio(self, base_size=500):
        height = self.pixmap().height()
        width = self.pixmap().width()
        if height > width:
            self.resize(base_size, base_size*self.aspect_ratio())
        else:
            self.resize(base_size*self.aspect_ratio(), base_size)

    def aspect_fit(self, size: QSize):
        scrollbar_pixel = 20
        if self.pixmap().width() > self.pixmap().height():
            self.scale_image((size.width()-scrollbar_pixel) / self.width())
        else:
            self.scale_image((size.height()-scrollbar_pixel) / self.height())
            print(self.factor)

    def aspect_ratio(self):
        width = self.pixmap().width()
        height = self.pixmap().height()
        return max(width, height) / min(width, height)

