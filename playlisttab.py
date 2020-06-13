import os

from PySide2.QtCore import (Qt, Signal, QPoint)
from PySide2.QtWidgets import (QApplication, QTabWidget, QInputDialog,
                               QMessageBox, QFileDialog, QMenu)
from playlistview import PlaylistView
from utility import dialog_for_message, createAction


class PlaylistTab(QTabWidget):

    double_clicked = Signal()
    playlist_ext = '.m3u8'

    def __init__(self, parent=None):
        super().__init__(parent)

        self.save_playlist_path = 'playlist/'

        self.addTab(self.create_new(), 'Queue')
        self.setCurrentIndex(0)
        self.setUsesScrollButtons(True)
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideNone)

        self.context_menu = QMenu(self)
        self.create_context_menu()

        self.currentChanged[int].connect(self.adjust_header_size)

        self.autoload_playlists()

        self.show()

    def create_context_menu(self):
        self.context_menu.addAction(createAction(self, 'Add Playlist', self.add_playlist))
        self.context_menu.addAction(createAction(self, 'Rename', self.rename_playlist))
        self.context_menu.addAction(createAction(self, 'Save', self.save_current))
        self.context_menu.addAction(createAction(self, 'Open', self.load_playlist))
        self.context_menu.addSeparator()
        self.context_menu.addAction(createAction(self, 'Remove Playlist', self.remove_playlist))

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def url(self, index=0):
        self.playListView.url(index)

    def open(self):
        self.widget(self.currentIndex()).open()

    def open_directory(self):
        self.currentWidget().open_directory()

    def current_playlist(self):
        return self.currentWidget()

    def add_playlist(self, title=''):
        if title and not self.is_used(title):
            self.addTab(self.create_new(), title)
            return True
        while True:
            title, ok = QInputDialog.getText(self, 'New Playlist name', 'New Playlist name')
            if not ok or not title:
                return False
            elif self.is_used(title):
                msg_box = dialog_for_message("'{0}' is already used.".format(title))
                msg_box.exec()
            else:
                self.addTab(self.create_new(), title)
                return True

    def create_new(self):
        new = PlaylistView(self)
        new.playlist_double_clicked.connect(self.handle_playlist_double_clicked)
        return new

    def rename_playlist(self):
        original = self.tabText(self.currentIndex())
        while True:
            title, ok = QInputDialog.getText(self, 'Rename Playlist', 'New Playlist name', text=original)
            if not ok or not title:
                return False
            elif self.is_used(title):
                msg_box = dialog_for_message("'{0}' is already used.".format(title))
                msg_box.exec()
            else:
                self.setTabText(self.currentIndex(), title)
                return True

    def remove_playlist(self):
        if self.count() == 1:
            msg_box = dialog_for_message("You can't remove the last tab.")
            msg_box.exec()
            return

        current = self.currentIndex()
        title = self.tabText(current)
        msg_box = dialog_for_message('Do you want to remove \'{0}\' permanently?'.format(title),
                                     QMessageBox.Cancel | QMessageBox.Ok)
        ret = msg_box.exec()
        if ret == QMessageBox.Ok:
            self.remove_file(title)
            self.removeTab(current)
            return title

    def remove_file(self, name=''):
        if os.path.exists('./' + self.save_playlist_path + name):
            os.remove('./' + self.save_playlist_path + name)
            return name
        return False

    def save_current(self):
        """現在のPlaylistを保存する

        タイトルをファイル名として、パスをファイルの各行に書き出す。
        """
        name = self.tabText(self.currentIndex())
        url, ok = QFileDialog.getSaveFileUrl(
            self, 'Save File', name+self.playlist_ext, 'playlist(*{}'.format(self.playlist_ext))
        if not ok:
            return False
        url = url.toLocalFile()
        self.current_playlist().save(url)

    def save_all(self):
        """すべてのプレイリストを保存する"""
        os.makedirs(self.save_playlist_path, exist_ok=True)
        for i in range(self.count()):
            title = self.tabText(i)
            if not title == 'Queue':
                path = self.save_playlist_path + self.tabText(i) + self.playlist_ext
                self.widget(i).save(path)

    def load_playlist(self):
        """ファイルを開いて、タブを追加する"""
        url, ok = QFileDialog.getOpenFileUrl(self, 'open a playlist files', filter='*.m3u *.m3u8')
        if not ok:
            return
        file_name = url.fileName()
        file_name = file_name[:file_name.find('.')]  # remove extension from file_name
        if self.is_used(file_name):
            return
        new_playlist = self.create_new()
        self.addTab(new_playlist, file_name)
        new_playlist.load(url.toLocalFile())
        self.setCurrentIndex(self.count()-1)

    def remove_files(self):
        """すべてのプレイリストファイルを消去する"""
        import shutil
        shutil.rmtree(self.save_playlist_path)

    def autoload_playlists(self):
        """プレイリストをフォルダから読み込む。

        デフォルトではplaylist/から読み込もうとする。"""
        import os.path

        path = 'playlist/'
        if not os.path.exists(path):
            return False
        files = os.listdir(path)

        for file in files:
            if os.path.isdir(file) or 'm3u' not in file[-4:]:
                continue
            new_playlist = self.create_new()
            self.addTab(new_playlist, file[:file.find('.')])
            new_playlist.load(path+file)

        return True

    def is_valid_name(self, name):
        if len(name) and not self.is_used():
            return True
        return False

    def is_used(self, name):
        for i in range(self.count()):
            if name == self.tabText(i):
                return True
        return False

    def delete_items(self):
        self.currentWidget().delete_items()

    def handle_playlist_double_clicked(self):
        self.double_clicked.emit()

    def next_tab(self):
        i = self.currentIndex()
        if i == self.count()-1:
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(i+1)

    def previous_tab(self):
        i = self.currentIndex()
        if i == 0:
            self.setCurrentIndex(self.count()-1)
        else:
            self.setCurrentIndex(i-1)

    def adjust_header_size(self):
        """adjust header size
        :return: Nothing
        """
        if self.parent().parent().parent().parent().adjust_header_act.isChecked():
            self.currentWidget().auto_resize_header()

    def dragEnterEvent(self, event):
        '''whether accept drag or not.

        :param QDragEnterEvent event:
        :return: None
        '''
        if event.mimeData().hasUrls() and self.index_at(event.pos()) != self.currentIndex():
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """

        :param QDragMoveEvent event:
        :return:
        """
        if event.mimeData().hasUrls() and self.index_at(event.pos()) != self.currentIndex():
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Extract dropped data

        :param QDropEvent event: contains url list.
        :return:
        """
        index = self.index_at(event.pos())
        if index < 0:
            event.ignore()
        else:
            self.widget(index).add_items(event.mimeData().urls())
            event.acceptProposedAction()

    def index_at(self, pos):
        """return tab index.

        :param QPoint pos:
        :return int:
        """
        return self.tabBar().tabAt(pos - QPoint(self.left_space(), 0))

    def left_space(self):
        """Return left margin.

        :rtype int:
        """
        tabs_width = 0
        for i in range(self.count()):
            tabs_width += self.tabBar().tabRect(i).width()
        return (self.width() - tabs_width) / 2 if self.width() > tabs_width else 0


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = PlaylistTab()
    sys.exit(app.exec_())
