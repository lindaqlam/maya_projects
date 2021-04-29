from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ObjectRenamerDialog(QtWidgets.QDialog):

    WINDOW_TITLE = "Object Renamer"

    def __init__(self, parent=maya_main_window()):
        super(ObjectRenamerDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(300, 120)
        self.selection = cmds.ls(selection=True, long=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self): #
        self.help_action = QtWidgets.QAction("Help", self)

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()
        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction(self.help_action)

        self.divider_line = QtWidgets.QFrame()
        self.divider_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.divider_line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.divider_line.setLineWidth(1)
        self.divider_line.setMinimumHeight(3)

        # RENAME
        self.rename_le = QtWidgets.QLineEdit()
        self.rename_btn = QtWidgets.QPushButton("Go")
        self.rename_label = QtWidgets.QLabel("RENAME")

        # FIND AND REPLACE
        self.find_le = QtWidgets.QLineEdit()
        self.replace_le = QtWidgets.QLineEdit()
        self.find_replace_btn = QtWidgets.QPushButton("Go")
        self.find_replace_label = QtWidgets.QLabel("FIND AND REPLACE")

        # ADD PREFIX
        self.prefix_le = QtWidgets.QLineEdit()
        self.prefix_btn = QtWidgets.QPushButton("Go")
        self.prefix_label = QtWidgets.QLabel("PREFIX")

        # ADD SUFFIX
        self.suffix_le = QtWidgets.QLineEdit()
        self.suffix_btn = QtWidgets.QPushButton("Go")
        self.suffix_label = QtWidgets.QLabel("SUFFIX")

    def create_layout(self):
        rename_header = QtWidgets.QHBoxLayout()
        rename_header.addWidget(self.rename_label)
        rename_layout = QtWidgets.QHBoxLayout()
        rename_layout.addWidget(self.rename_le)
        rename_layout.addWidget(self.rename_btn)

        find_replace_header = QtWidgets.QHBoxLayout()
        find_replace_header.addWidget(self.find_replace_label)
        find_layout = QtWidgets.QHBoxLayout()
        find_layout.addWidget(self.find_le)
        replace_layout = QtWidgets.QHBoxLayout()
        replace_layout.addWidget(self.replace_le)
        replace_layout.addWidget(self.find_replace_btn)

        prefix_header = QtWidgets.QHBoxLayout()
        prefix_header.addWidget(self.prefix_label)
        prefix_layout = QtWidgets.QHBoxLayout()
        prefix_layout.addWidget(self.prefix_le)
        prefix_layout.addWidget(self.prefix_btn)

        suffix_header = QtWidgets.QHBoxLayout()
        suffix_header.addWidget(self.suffix_label)
        suffix_layout = QtWidgets.QHBoxLayout()
        suffix_layout.addWidget(self.suffix_le)
        suffix_layout.addWidget(self.suffix_btn)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("", rename_header)
        form_layout.addRow("New Name:", rename_layout)
        form_layout.addWidget(self.divider_line)
        form_layout.addRow("", find_replace_header)
        form_layout.addRow("Find:", find_layout)
        form_layout.addRow("Replace:", replace_layout)
        form_layout.addWidget(self.divider_line)
        form_layout.addRow("", prefix_header)
        form_layout.addRow("Add Prefix", prefix_layout)
        form_layout.addWidget(self.divider_line)
        form_layout.addRow("", suffix_header)
        form_layout.addRow("Add Suffix", suffix_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(form_layout)

    def create_connections(self):
        self.help_action.triggered.connect(self.help_tool)

        # RENAME
        self.rename_btn.clicked.connect(self.rename_obj)

        # FIND AND REPLACE
        self.find_replace_btn.clicked.connect(self.find_replace)

        # ADD PREFIX
        self.prefix_btn.clicked.connect(self.add_prefix)

        # ADD PREFIX
        self.suffix_btn.clicked.connect(self.add_suffix)

    def rename_obj(self):
        new_name = self.rename_le.text()

        for obj in self.selection:
            original_name = obj.split('|')[-1]
            actual_name = cmds.rename(obj, new_name)

    def find_replace(self):
        find_str = self.find_le.text()
        replace_str = self.replace_le.text()

        for obj in self.selection:
            original_name = obj.split('|')[-1]
            new_name = original_name.replace(find_str, replace_str) or original_name
            actual_name = cmds.rename(obj, new_name)

    def add_prefix(self):
        prefix = self.prefix_le.text()

        for obj in self.selection:
            original_name = obj.split('|')[-1]
            new_name = prefix + original_name
            actual_name = cmds.rename(obj, new_name)

    def add_suffix(self):
        suffix = self.suffix_le.text()

        for obj in self.selection:
            original_name = obj.split('|')[-1]
            new_name = original_name + suffix
            actual_name = cmds.rename(obj, new_name)

    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.help_action)

        context_menu.exec_(self.mapToGlobal(point))

    def help_tool(self):
        QtWidgets.QMessageBox.about(self, "About Object Renamer", "Rename a single object or multiple objects in batch by first selecting all relevant objects before running the tool.")

if __name__ == "__main__":

    try:
        object_renamer.close() # pylint: disable=E0601
        object_renamer.deleteLater()
    except:
        pass

    object_renamer = ObjectRenamerDialog()
    object_renamer.show()
