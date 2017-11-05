from ensurepip import __main__

from PyQt5.QtCore import QDir
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QApplication, QSizePolicy, QFileDialog

from imageviewer import ImageViewer


class Viewer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.image_list = []
        self.index = 0
        self.filters = []
        self.init_filters()

        self.image_viewer = ImageViewer()
        self.image_viewer.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_viewer)
        self.scroll_area.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def init_filters(self):
        formats = QImageReader.supportedImageFormats()
        for f in formats:
            self.filters.append('*.' + f.data().decode('utf-8'))

    def init_action(self):
        pass

    def open_directory(self, path=''):
        if not path:
            path = QFileDialog.getExistingDirectory(self, 'Open Directory',
                                                    '.', QFileDialog.ShowDirsOnly)
        directory = QDir(path)
        directory.setNameFilters(self.filters)
        image_files = directory.entryList()
        for file in image_files:
            self.add_item(directory.absolutePath() + '/' + file)

    def add_item(self, path=''):
        if path:
            self.image_list.append(path)

    def set_image(self, index):
        if index < 0 or index >= len(self.image_list):
            return None
        self.image_viewer.load_image(self.image_list[index])
        self.index = index
        self.show()

    def next(self):
        self.set_image(self.index+1)

    def previous(self):
        self.set_image(self.index-1)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    viewer = Viewer()
    viewer.open_directory()
    viewer.resize(400, 400 * viewer.image_viewer.aspect_ratio())
    viewer.set_image(1)
    sys.exit(app.exec_())
