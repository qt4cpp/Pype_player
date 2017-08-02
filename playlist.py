from venv import create

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication

from playlisttab import PlaylistTab
from playlistview import PlaylistView
from utility import make_button_from_fa, createAction


class Playlist(QWidget):

    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)
        
        self.playlist_tab = PlaylistTab()
        self.playlist_tab.double_clicked.connect(self.handle_double_clicked)
        self.using_playlist: PlaylistView = self.playlist_tab.widget(0)

        self.add_playlist_button = make_button_from_fa('fa.plus', tooltip='Add new playlist')
        self.add_playlist_button.clicked.connect(self.playlist_tab.add_playlist)
        self.remove_playlist_button = make_button_from_fa('fa.minus', tooltip='Remove current playlist')
        self.remove_playlist_button.clicked.connect(self.playlist_tab.remove_playlist)
        self.open_directory_button = make_button_from_fa('fa.folder-open-o', tooltip='Add media files from directory')
        self.open_directory_button.clicked.connect(self.open_directory)
        self.add_file_button = make_button_from_fa('fa.file-o', tooltip='Add media file')
        self.add_file_button.clicked.connect(self.open)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_playlist_button)
        button_layout.addWidget(self.remove_playlist_button)
        button_layout.addWidget(self.open_directory_button)
        button_layout.addWidget(self.add_file_button)
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

        add_file = createAction(self, 'Add file(s)', self.open, 'Ctrl+o')
        open_directory = createAction(self, 'Open directory', self.open_directory, 'Ctrl+Shift+o')

        add_playlist = createAction(self, 'Add playlist',
                                    self.playlist_tab.add_playlist, 'Ctrl+N')
        rename_playlist = createAction(self, 'Rename Playlist',
                                       self.playlist_tab.rename_playlist)
        remove_playlist = createAction(self, 'Remove Playlist',
                                       self.playlist_tab.remove_playlist)
        save_playlist = createAction(self, 'Save current Playlist',
                                     self.playlist_tab.save_current, 'Ctrl+s')
        load_playlist = createAction(self, 'Load playlist file', self.playlist_tab.load_playlist, 'Ctrl+l')

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(add_file)
        file_menu.addAction(open_directory)
        file_menu.addSeparator()
        file_menu.addAction(add_playlist)
        file_menu.addAction(rename_playlist)
        file_menu.addAction(remove_playlist)
        file_menu.addAction(save_playlist)
        file_menu.addAction(load_playlist)

    def playlist(self):
        return self.playlist_tab.current_playlist()

    def open(self):
        self.playlist().open()

    def open_directory(self):
        self.playlist().open_directory()

    def get_new_one(self):
        self.using_playlist = self.playlist()
        selected_url = self.using_playlist.selected()
        if selected_url:
            self.using_playlist.set_current_index(selected_url)
        elif not self.using_playlist.current_index.isValid():
            self.using_playlist.set_current_index_from_row(0)
        return self.current_item()

    def current_item(self):
        return self.using_playlist.current()

    def next(self):
        return self.using_playlist.next()

    def previous(self):
        pass

    def current_row(self):
        return self.using_playlist.current_row()

    def first(self):
        self.using_playlist.set_current_index_from_row(0)
        return self.current_item()

    def count(self):
        return self.using_playlist.count()

    def update_listview(self):
        self.using_playlist.selectAll()
        self.using_playlist.clearSelection()

    def disable_current_index(self):
        self.using_playlist.set_current_index_from_row(-1)

    def handle_double_clicked(self):
        self.using_playlist = self.playlist()
        self.double_clicked.emit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())
