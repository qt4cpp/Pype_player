from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication

from playlisttab import PlaylistTab
from utility import make_button_from_fa, createAction


class Playlist(QWidget):

    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)
        
        self.playlist_tab = PlaylistTab()
        self.playlist_tab.double_clicked.connect(self.handle_double_clicked)
        self.using_playlist = self.playlist_tab.widget(0)

        self.add_playlist_button = make_button_from_fa('fa.clone')
        self.add_playlist_button.clicked.connect(self.playlist_tab.add_playlist)
        self.open_directory_button = make_button_from_fa('fa.folder-open-o')
        self.open_directory_button.clicked.connect(self.playlist_tab.open_directory)
        self.add_file_button = make_button_from_fa('fa.plus')
        self.add_file_button.clicked.connect(self.playlist_tab.open)
        self.delete_file_button = make_button_from_fa('fa.minus')

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_playlist_button)
        button_layout.addWidget(self.open_directory_button)
        button_layout.addWidget(self.add_file_button)
        button_layout.addWidget(self.delete_file_button)
        button_layout.setSpacing(0)

        layout = QVBoxLayout()
        layout.addWidget(self.playlist_tab)
        layout.addLayout(button_layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.show()

    def create_menu(self, menubar=None):
        if menubar is None:
            return

        openFile = createAction(self, 'Open', self.open, 'Ctrl+o')

        add_playlist = createAction(self, 'Add playlist',
                                    self.playlist_tab.add_playlist, 'Ctrl+N')
        rename_playlist = createAction(self, 'Rename Playlist',
                                       self.playlist_tab.rename_playlist)
        remove_playlist = createAction(self, 'Remove Playlist',
                                       self.playlist_tab.remove_playlist)
        save_playlist = createAction(self, 'Save current Playlist',
                                     self.playlist_tab.save_current, 'Ctrl+s')

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(openFile)
        file_menu.addSeparator()
        file_menu.addAction(add_playlist)
        file_menu.addAction(rename_playlist)
        file_menu.addAction(remove_playlist)
        file_menu.addAction(save_playlist)

    def playlist(self):
        return self.playlist_tab.current_playlist()

    def open(self):
        self.playlist_tab.open()

    def current_item(self):
        return self.using_playlist.current()

    def next(self):
        return self.using_playlist.next()

    def previous(self):
        pass

    def count(self):
        return self.using_playlist.count()

    def handle_double_clicked(self):
        self.using_playlist = self.playlist()
        self.double_clicked.emit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())
