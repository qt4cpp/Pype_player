from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMenuBar, QMenu


class MenuController(QObject):

    @property
    def menubar(self):
        return self._menubar

    def __init__(self, parent=None, menubar: QMenuBar=None):
        super().__init__(parent)

        self._menubar = menubar
        self.registered_menu = {}

    def register(self, hierarchy, action):
        menu = self.menu(hierarchy)
        menu.addAction(action)

    def register_list(self, hierarchy, action_list):
        for action in action_list:
            self.register(hierarchy, action)

    def menu(self, hierarchy):
        """入力例(File/Settings/Keybinds) ->
        File - Settings - Keybinds のQMenuを返す
        """
        title  = hierarchy.split('/', maxsplit=1)[0]
        if title in self.registered_menu:
            top_menu = self.registered_menu[title]
        else:
            top_menu = self.add_new_menu(self._menubar, title)
        if len(hierarchy) == 1:
            return top_menu

        self.hierarchic_menu(top_menu, hierarchy)
        return self.registered_menu[hierarchy]

    def add_new_menu(self, menu, hierarchy) -> QMenu:
        """menu に name で渡された名前の"""
        name = hierarchy.rsplit('/')[-1]
        new = menu.addMenu(name)
        self.registered_menu[hierarchy] = new
        return new

    def hierarchic_menu(self, top_menu: QMenu, hierarchy: str):
        if self.is_exist(hierarchy):
            return self.registered_menu[hierarchy]
        if '/' in hierarchy:
            higher = hierarchy.rsplit('/', 1)[0]
            self.hierarchic_menu(top_menu, higher)
            self.add_new_menu(self.registered_menu[higher], hierarchy)
        else:
            self.add_new_menu(top_menu, hierarchy)
        return self.registered_menu[hierarchy]

    def is_exist(self, hierarchy):
        return hierarchy in self.registered_menu

    def search(self, menu_list, name) -> QMenu:
        for menu in menu_list:
            if menu.title() == name:
                return menu
        return None
