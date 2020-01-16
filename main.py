import sys

from PySide2.QtWidgets import QMainWindow, QApplication

from menu_controller import MenuController
from player import Player
from utility import createAction
from viewer import Viewer


class PypePlayer(QMainWindow):

    def __init__(self, parent=None):
        super(PypePlayer, self).__init__(parent)

        self.player = Player(parent=self)
        self.setCentralWidget(self.player)
        self.viewer = Viewer(parent=self)

        self.menu_controller = MenuController(self, self.menuBar())
        self.create_menu()
        self.update_actions()

        self.player.media_loaded.connect(self.set_window_title)
        self.player.stopped.connect(self.set_window_title)

        self.resize(600, 360)
        self.set_window_title('')
        self.show()
        self.adjust_header_act.trigger()

    def create_menu(self):

        # Player
        forward_short = createAction(self.player, 'Short Forward', self.player.forward_short, 'Right')
        forward_medium = createAction(self.player, 'Forward', self.player.forward_medium, 'Shift+Right')
        forward_long = createAction(self.player, 'Long Forward', self.player.forward_long, 'Ctrl+Right')
        backward_short = createAction(self.player, 'Short Backward', self.player.backward_short, 'Left')
        backward_medium = createAction(self.player, 'Backward', self.player.backward_medium, 'Shift+Left')
        backward_long = createAction(self.player, 'Long Backward', self.player.backward_long, 'Ctrl+Left')

        play_and_pause = createAction(self.player, 'Play', self.player.optimal_play, 'Space')
        stop = createAction(self.player, 'Stop', self.player.stop, 'Ctrl+.')

        self.menu_controller.add_action_list('Playback', [play_and_pause, stop])
        self.menu_controller.add_action_list('Playback/Jump',
                                   [forward_short, forward_medium, forward_long])
        self.menu_controller.add_separator('Playback/Jump')
        self.menu_controller.add_action_list('Playback/Jump',
                                   [backward_short, backward_medium, backward_long])

        load_and_play = createAction(self.player, 'Load and Play', self.player.load_and_play, 'Return')
        self.player.addAction(load_and_play)
        self.player.context_menu.addActions([play_and_pause, stop])

        # Playlist
        playlist = self.player.playlist
        add_file = createAction(playlist, 'Add file(s)', playlist.open, 'Ctrl+o')
        open_directory = createAction(playlist, 'Open directory', playlist.open_directory, 'Ctrl+Shift+o')

        add_playlist = createAction(playlist, 'New', playlist.playlist_tab.add_playlist, 'Ctrl+N')
        load_playlist = createAction(playlist, 'Load', playlist.playlist_tab.load_playlist, 'Ctrl+l')
        save_playlist = createAction(playlist, 'Save Current', playlist.playlist_tab.save_current, 'Ctrl+s')
        rename_playlist = createAction(playlist, 'Rename', playlist.playlist_tab.rename_playlist)
        remove_playlist = createAction(playlist, 'Remove Current', playlist.playlist_tab.remove_playlist)

        next_tab_act = createAction(playlist, 'Next Tab', playlist.playlist_tab.next_tab, 'Meta+tab')
        previous_tab_act = createAction(playlist, 'Previous Tab', playlist.playlist_tab.previous_tab, 'Meta+Shift+tab')

        self.adjust_header_act = createAction(playlist, 'Auto Adjust Header', playlist.playlist_tab.adjust_header_size)
        self.adjust_header_act.setCheckable(True)

        self.menu_controller.add_action_list('File', [add_file, open_directory])
        self.menu_controller.add_separator('File')
        self.menu_controller.add_action_list('Playlist',
                                             [add_playlist, load_playlist, rename_playlist,save_playlist,
                                              remove_playlist])
        self.menu_controller.add_separator('Playlist')
        self.menu_controller.add_action_list('Playlist', [next_tab_act, previous_tab_act, self.adjust_header_act])

        # Viewer
        set_reference_act = createAction(self.viewer, 'Set Reference', self.viewer.set_reference)
        next_act = createAction(self.viewer, 'next', self.viewer.next, 'Alt+Right')
        previous_act = createAction(self.viewer, 'previous', self.viewer.previous, 'Alt+Left')
        zoom_in_act = createAction(self.viewer, 'Zoom In', self.viewer.zoom_in, 'Ctrl++')
        zoom_out_act = createAction(self.viewer, 'Zoom Out', self.viewer.zoom_out, 'Ctrl+-')
        normal_size_act = createAction(self.viewer, 'Normal size', self.viewer.normal_size, 'Ctrl+0')
        fit_to_window_act = createAction(self.viewer, 'Fit to window', self.viewer.fit_to_window)
        fit_to_window_act.setCheckable(True)
        show_act = createAction(self.viewer, 'Show', self.viewer.show)
        close_window_act = createAction(self.viewer, 'Close', self.viewer.hide, 'Ctrl+c')
        self.viewer_act = [set_reference_act, next_act, previous_act, zoom_in_act, zoom_out_act, normal_size_act,
                           fit_to_window_act, show_act, close_window_act]
        self.viewer.context_menu.addActions(self.viewer_act)
        self.menu_controller.add_action_list('Viewer', self.viewer_act)

    def set_window_title(self, str=''):
        if str:
            self.setWindowTitle('{0} - Pype Player'.format(str))
        else:
            self.setWindowTitle('Pype Player')

    def closeEvent(self, event):
        self.player.playlist.save_all()
        super(PypePlayer, self).closeEvent(event)

    def update_actions(self):
        for a in self.viewer_act[1:]:
            a.setEnabled(self.viewer.isReady())

if __name__ == '__main__':
    app = QApplication(sys.argv)

    pypePlayer = PypePlayer()
    sys.exit(app.exec_())
