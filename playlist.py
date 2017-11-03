from venv import create

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QApplication, QMenu

from playlisttab import PlaylistTab
from playlistview import PlaylistView
from utility import make_button_from_fa, createAction


class Playlist(QWidget):

    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)

        self.playlist_tab = PlaylistTab(parent=self)
        self.playlist_tab.double_clicked.connect(self.handle_double_clicked)
        self.using_playlist: PlaylistView = self.playlist_tab.widget(0)

        layout = QVBoxLayout()
        layout.addWidget(self.playlist_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.show()
        print(self.width())

    def create_menu(self, controller):
        if controller is None:
            return

        add_file = createAction(self, 'Add file(s)', self.open, 'Ctrl+o')
        open_directory = createAction(self, 'Open directory', self.open_directory, 'Ctrl+Shift+o')

        add_playlist = createAction(self, 'New Playlist', self.playlist_tab.add_playlist, 'Ctrl+N')
        load_playlist = createAction(self, 'Load Playlist file', self.playlist_tab.load_playlist, 'Ctrl+l')
        rename_playlist = createAction(self, 'Rename Playlist', self.playlist_tab.rename_playlist)
        save_playlist = createAction(self, 'Save Current Playlist', self.playlist_tab.save_current, 'Ctrl+s')
        remove_playlist = createAction(self, 'Remove Playlist', self.playlist_tab.remove_playlist)

        next_tab_act = createAction(self, 'Next Tab', self.playlist_tab.next_tab, 'Meta+tab')
        previous_tab_act = createAction(self, 'Preivous Tab', self.playlist_tab.previous_tab, 'Meta+Shift+tab')

        controller.add_action_list('File', [add_file, open_directory])
        controller.add_action_list('Playlist', [next_tab_act, previous_tab_act])
        controller.add_separator('Playlist')
        controller.add_action_list('Playlist',
                                   [add_playlist, load_playlist, rename_playlist, save_playlist, remove_playlist])

    def playlist(self):
        return self.playlist_tab.current_playlist()

    def resizeEvent(self, event):
        self.playlist_tab.currentWidget().resizeHeaderWidth(self.width()-10)
        super().resizeEvent(event)

    def change_using_playlist(self):
        self.using_playlist.deactivate()
        self.using_playlist = self.playlist()

    def open(self):
        self.playlist().open()

    def open_directory(self):
        self.playlist().open_directory()

    def get_new_one(self):
        if self.using_playlist is not self.playlist():
            self.change_using_playlist()
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
        return self.using_playlist.previous()

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
        self.change_using_playlist()
        self.double_clicked.emit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())
