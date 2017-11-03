from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel


class ImageViewer(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)

        pixmap = self.load_image('test/image/duo-270.png')
        self.setPixmap(pixmap)
        print(pixmap.height(), pixmap.width())
        print(self.aspect_ratio(pixmap))

        self.resize(400, 500)
        self.show()

    def load_image(self, path='', ):
        # check file exists
        pixmap = QPixmap()
        pixmap.load(path)
        return pixmap

    def aspect_ratio(self, pixmap: QPixmap):
        height = pixmap.height()
        width = pixmap.width()
        return max(height, width) / min(height, width)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = ImageViewer()
    sys.exit(app.exec_())