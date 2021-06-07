from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMaya as om
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class OpenImportDialog(QtWidgets.QDialog):

    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"

    selected_filter = "Maya (*ma *.mb)"

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = OpenImportDialog()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(OpenImportDialog, self).__init__(parent)

        self.setWindowTitle("Open/Import/Reference")
        self.setMinimumSize(300, 300)

        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)


        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.file_path_label = QtWidgets.QLabel("Open/Import/Reference File")

        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton()
        self.select_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_file_path_btn.setToolTip("Select File")

        self.open_rb = QtWidgets.QRadioButton("Open")
        self.open_rb.setChecked(True)
        self.import_rb = QtWidgets.QRadioButton("Import")

        self.force_cb = QtWidgets.QCheckBox("Force")

        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.save_btn = QtWidgets.QPushButton("Save")

        self.save_scene_label = QtWidgets.QLabel("Save Scene")

        self.location_le = QtWidgets.QLineEdit()

        self.ma_type = QtWidgets.QRadioButton(".ma")
        self.ma_type.setChecked(True)
        self.mb_type = QtWidgets.QRadioButton(".mb")

        self.save_file_path_btn = QtWidgets.QPushButton()
        self.save_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.save_file_path_btn.setToolTip("Select File")

        self.save_le = QtWidgets.QLineEdit()


    def create_layout(self):
        label1 = QtWidgets.QHBoxLayout()
        label1.addWidget(self.file_path_label)

        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.select_file_path_btn)

        radio_btn_layout = QtWidgets.QHBoxLayout()
        radio_btn_layout.addWidget(self.open_rb)
        radio_btn_layout.addWidget(self.import_rb)

        apply_btn_layout = QtWidgets.QHBoxLayout()
        apply_btn_layout.addStretch()
        apply_btn_layout.addWidget(self.apply_btn)

        label2 = QtWidgets.QHBoxLayout()
        label2.addWidget(self.save_scene_label)

        location_layout = QtWidgets.QHBoxLayout()
        location_layout.addWidget(self.location_le)
        location_layout.addWidget(self.save_file_path_btn)

        save_layout = QtWidgets.QHBoxLayout()
        save_layout.addWidget(self.save_le)

        file_type_btn_layout = QtWidgets.QHBoxLayout()
        file_type_btn_layout.addWidget(self.ma_type)
        file_type_btn_layout.addWidget(self.mb_type)


        divider = QtWidgets.QFrame()
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        divider.setLineWidth(3)
        divider.setStyleSheet("margin-bottom: 55px")

        save_btn_layout = QtWidgets.QHBoxLayout()
        save_btn_layout.addStretch()
        save_btn_layout.addWidget(self.save_btn)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("", label1)
        form_layout.addRow("File:", file_path_layout)
        form_layout.addRow("", radio_btn_layout)
        form_layout.addRow("", self.force_cb)
        form_layout.addRow("", apply_btn_layout)
        form_layout.addRow("", label2)
        form_layout.addRow("Location:", location_layout)
        form_layout.addRow("Save As:", save_layout)
        form_layout.addRow("", file_type_btn_layout)
        form_layout.addRow("", save_btn_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)

    def create_connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)
        self.save_file_path_btn.clicked.connect(self.show_location_select_dialog)
        self.save_btn.clicked.connect(self.save_scene)

        self.open_rb.toggled.connect(self.update_force_visibility)

        self.apply_btn.clicked.connect(self.load_file)

    def show_file_select_dialog(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        if file_path:
            self.filepath_le.setText(file_path)

    def show_location_select_dialog(self):
        dir = QtWidgets.QFileDialog.getExistingDirectoryUrl(self, "Select Directory", "")
        if dir:
            self.location_le.setText(QtCore.QUrl.toString(dir))

    def update_force_visibility(self, checked):
        self.force_cb.setVisible(checked)

    def load_file(self):
        file_path = self.filepath_le.text()
        if not file_path:
            return

        file_info = QtCore.QFileInfo(file_path)
        if not file_info.exists():
            om.MGlobal.displayError("File does not exist: {0}".format(file_path))
            return

        if self.open_rb.isChecked():
            self.open_file(file_path)
        elif self.import_rb.isChecked():
            self.import_file(file_path)
        else:
            self.reference_file(file_path)

    def open_file(self, file_path):
        force = self.force_cb.isChecked()
        if not force and cmds.file(q=True, modified=True):
            result = QtWidgets.QMessageBox.question(self, "Modified", "Current scene has unsaved changes. Continue?")
            if result == QtWidgets.QMessageBox.StandardButton.Yes:
                force = True
            else:
                return

        cmds.file(file_path, open=True, ignoreVersion=True, force=force)

    def import_file(self, file_path):
        cmds.file(file_path, i=True, ignoreVersion=True)

    def reference_file(self, file_path):
        cmds.file(file_path, reference=True, ignoreVersion=True)

    def save_scene(self):
        if self.ma_type.isChecked():
            file_type = "mayaAscii"
            print "mayaAscii"
        else:
            file_type = "mayaBinary"
            print "mayaBinary"


        location = self.location_le.text()[7:]
        file_name = self.save_le.text()
        file_path = location + '/' + file_name

        cmds.file( rename=file_path )
        cmds.file( save=True, force=True, type=file_type )

if __name__ == "__main__":

    try:
        open_import_dialog.close() # pylint: disable=E0601
        open_import_dialog.deleteLater()
    except:
        pass

    open_import_dialog = OpenImportDialog()
    open_import_dialog.show()


