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

    def scale_image_by_rate(self, rate):
        if self.factor * rate > 4.76:
            self.factor = 4.76
        elif self.factor * rate < 0.1:
            self.factor = 0.1
        else:
            self.factor = round(rate * self.factor, 2)
        self.scale_image_by_factor(self.factor)
        print(self.factor)

    def scale_image_by_factor(self, factor):
        if factor > 4.76:
            factor = 4.76
        elif factor < 0.1:
            factor = 0.1
        self.factor = factor
        self.resize(self.factor * self.pixmap().size())

    def resize_keep_aspect_ratio(self, base_size=500):
        height = self.pixmap().height()
        width = self.pixmap().width()
        if height > width:
            self.resize(base_size, base_size*self.aspect_ratio())
        else:
            self.resize(base_size*self.aspect_ratio(), base_size)

    def aspect_fit(self, size: QSize):
        win_gradient = size.height() / size.width()
        pix_gradient = self.pixmap().height() / self.pixmap().width()
        if win_gradient > pix_gradient:
            self.resize(size.width(), int(size.width() * pix_gradient))
            self.factor = round(size.width() / self.pixmap().width(), 2)
        else:
            self.resize(int(size.height() / pix_gradient), size.height())
            self.factor = round(size.height() / self.pixmap().height(), 2)

    def aspect_ratio(self):
        width = self.pixmap().width()
        height = self.pixmap().height()
        return max(width, height) / min(width, height)

