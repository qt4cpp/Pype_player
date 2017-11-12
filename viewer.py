from ensurepip import __main__

from PyQt5.QtCore import QDir, pyqtSignal
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QApplication, QSizePolicy, QFileDialog, QAction, QMenu

from imageviewer import ImageViewer
from utility import createAction


class Viewer(QWidget):
    pix_is_ready = pyqtSignal()

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

        self.context_menu = QMenu(self)
        #self.create_menus()

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        self.pix_is_ready.connect(self.show)

    def init_filters(self):
        formats = QImageReader.supportedImageFormats()
        for f in formats:
            self.filters.append('*.' + f.data().decode('utf-8'))

    def create_menus(self, controller):
        viewer_act = []
        next_act = createAction(self, 'next', self.next, 'Alt+Right')
        previous_act = createAction(self, 'previous', self.previous, 'Alt+Left')
        zoom_in_act = createAction(self, 'Zoom In', self.zoom_in, 'Ctrl++')
        zoom_out_act = createAction(self, 'Zoom Out', self.zoom_out, 'Ctrl+-')
        normal_size_act = createAction(self, 'Normal size', self.normal_size, 'Ctrl+0')
        fit_window_act = createAction(self, 'Fit window', self.fit_to_window, 'Ctrl+l')
        show_act = createAction(self, 'Show', self.show)
        close_window_act = createAction(self, 'Close', self.close, 'Ctrl+c')
        viewer_act = [next_act, previous_act, zoom_in_act, zoom_out_act, normal_size_act,
             fit_window_act, show_act, close_window_act]
        self.context_menu.addActions(viewer_act)
        controller.add_action_list('Viewer', viewer_act)

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def setup(self):
        if not self.image_list:
            self.open_directory()
        if not self.image_viewer.pixmap():
            self.set_image(0)
        self.show()

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
        self.index = index
        self.pix_is_ready.emit()

    def next(self):
        self.set_image(self.index+1)
        self.image_viewer.scale_image_by_factor(self.image_viewer.factor)

    def previous(self):
        self.set_image(self.index-1)
        self.image_viewer.scale_image_by_factor(self.image_viewer.factor)

    def zoom_in(self):
        self.image_viewer.scale_image_by_rate(1.25)

    def zoom_out(self):
        self.image_viewer.scale_image_by_rate(0.8)

    def normal_size(self):
        self.image_viewer.adjustSize()
        self.image_viewer.factor = 1.0

    def fit_to_window(self):
        self.image_viewer.aspect_fit(self.scroll_area.size())

    def visible(self):
        if not self.image_viewer.pixmap():
            if self.image_list:
                self.set_image(0)
            else:
                self.open_directory()
                self.set_image(0)
            self.image_viewer.adjustSize()
        self.setVisible(True)

    def close(self):
        self.hide()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    viewer = Viewer()
    viewer.open_directory()
    viewer.set_image(0)
    sys.exit(app.exec_())
