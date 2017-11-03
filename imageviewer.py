from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel


class ImageViewer(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)

    def load_image(self, path='', ):
        # check file exists
        pixmap = QPixmap()
        pixmap.load(path)
        # check null
        self.setPixmap(pixmap)
        return pixmap

    def resize_keep_aspect_ratio(self, base_size=500):
        pixmap = self.pixmap()
        height = pixmap.height()
        width = pixmap.width()
        if height > width:
            self.resize(base_size, base_size*self.aspect_ratio(height, width))
        else:
            self.resize(base_size*self.aspect_ratio(height, width), base_size)

    def aspect_ratio(self, height, width):
        return max(height, width) / min(height, width)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    image_viewer = ImageViewer()
    image_viewer.load_image('test/image/duo-270.png')
    image_viewer.resize_keep_aspect_ratio(base_size=600)
    image_viewer.show()
    sys.exit(app.exec_())