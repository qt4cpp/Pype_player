from ensurepip import __main__

from PyQt5.QtCore import QDir
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QApplication, QSizePolicy, QFileDialog, QAction, QMenu

from imageviewer import ImageViewer
from utility import createAction


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
        #self.scroll_area.setWidgetResizable(True)

        self.context_menu = QMenu(self)
        self.create_actions()

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def init_filters(self):
        formats = QImageReader.supportedImageFormats()
        for f in formats:
            self.filters.append('*.' + f.data().decode('utf-8'))

    def create_actions(self):
        next_act = createAction(self, 'next', self.next, 'Alt+Right')
        previous_act = createAction(self, 'previous', self.previous, 'Alt+Left')
        zoom_in_act = createAction(self, 'Zoom In', self.zoom_in, 'Ctrl++')
        zoom_out_act = createAction(self, 'Zoom Out', self.zoom_out, 'Ctrl+-')
        normal_size_act = createAction(self, 'Normal size', self.normal_size, 'Ctrl+0')
        fit_window_act = createAction(self, 'Fit window', self.fit_to_window, 'Ctrl+l')
        self.context_menu.addActions(
            [next_act, previous_act, zoom_in_act, zoom_out_act, normal_size_act,
             fit_window_act])

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

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
        self.image_viewer.set_image(self.image_list[index])
        self.image_viewer.adjustSize()
        self.index = index
        self.show()
        self.image_viewer.aspect_fit(self.scroll_area.size())

    def next(self, step=1):
        self.set_image(self.index+step)

    def previous(self, step=1):
        self.set_image(self.index-step)

    def zoom_in(self):
        self.image_viewer.scale_image(1.25)

    def zoom_out(self):
        self.image_viewer.scale_image(0.8)

    def normal_size(self):
        self.image_viewer.adjustSize()
        self.image_viewer.factor = 1.0

    def fit_to_window(self):
        self.image_viewer.aspect_fit(self.scroll_area.size())

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    viewer = Viewer()
    viewer.open_directory()
    viewer.set_image(0)
    sys.exit(app.exec_())
