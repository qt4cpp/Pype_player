from PyQt5.QtWidgets import QAction, QWidget

def createAction(obj, name, function, shortcut=''):
    newAction = QAction(name, obj)
    newAction.setShortcut(shortcut)
    newAction.triggered.connect(function)

    return newAction
