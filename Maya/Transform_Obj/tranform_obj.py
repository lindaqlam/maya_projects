from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
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


class TransformTableDialog(QtWidgets.QDialog):

    #UserRole is integer value (0x0100) and is used as starting index for user defined data
    ATTR_ROLE = QtCore.Qt.UserRole
    VALUE_ROLE = QtCore.Qt.UserRole + 1

    def __init__(self, parent=maya_main_window()):
        super(TransformTableDialog, self).__init__(parent)

        self.setWindowTitle("Transform Object Table")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.table_wdg = QtWidgets.QTableWidget()
        self.table_wdg.setColumnCount(11)
        self.table_wdg.setColumnWidth(0,22)
        self.table_wdg.setColumnWidth(2,70)
        self.table_wdg.setColumnWidth(3,70)
        self.table_wdg.setColumnWidth(4,70)
        self.table_wdg.setColumnWidth(5,70)
        self.table_wdg.setColumnWidth(6,70)
        self.table_wdg.setColumnWidth(7,70)
        self.table_wdg.setColumnWidth(8,70)
        self.table_wdg.setColumnWidth(9,70)
        self.table_wdg.setColumnWidth(10,70)
        self.table_wdg.setHorizontalHeaderLabels(["", "Name", "TransX", "TransY", "TransZ", "RotateX", "RotateY", "RotateZ", "ScaleX", "ScaleY", "ScaleZ"])
        header_view = self.table_wdg.horizontalHeader()
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        self.file_name_le = QtWidgets.QLineEdit("file name")
        self.save_scene_btn = QtWidgets.QPushButton("Save Scene")
        self.clear_btn = QtWidgets.QPushButton("Clear Scene")
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.close_btn = QtWidgets.QPushButton("Close")

    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addStretch()
        button_layout.addWidget(self.file_name_le)
        button_layout.addWidget(self.save_scene_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.close_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.table_wdg)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.set_cell_changed_connection_enabled(True)

        self.save_scene_btn.clicked.connect(self.save_scene)
        self.clear_btn.clicked.connect(self.clear_scene)
        self.refresh_btn.clicked.connect(self.refresh_table)
        self.close_btn.clicked.connect(self.close)

    def set_cell_changed_connection_enabled(self, enabled):
        if enabled:
            self.table_wdg.cellChanged.connect(self.on_cell_changed)
        else:
            self.table_wdg.cellChanged.disconnect(self.on_cell_changed)

    def save_scene(self):
        file_name = self.file_name_le.text()

        cmds.file( rename=file_name )
        cmds.file( save=True, force=True, type='mayaAscii' )

    def clear_scene(self):
        cmds.select(all=True)
        cmds.delete()

    def showEvent(self, e):
        super(TransformTableDialog, self).showEvent(e)
        self.refresh_table()

    def keyPressEvent(self, e):
        super(TransformTableDialog, self).keyPressEvent(e)
        e.accept()

    def refresh_table(self):
        self.set_cell_changed_connection_enabled(False)

        self.table_wdg.setRowCount(0)

        meshes = cmds.ls(type="mesh")
        for i in range(len(meshes)):
            transform_name = cmds.listRelatives(meshes[i], parent=True)[0]
            translation = cmds.getAttr("{0}.translate".format(transform_name))[0]
            visible = cmds.getAttr("{0}.visibility".format(transform_name))

            rotation = cmds.getAttr("{0}.rotate".format(transform_name))[0]

            scale = cmds.getAttr("{0}.scale".format(transform_name))[0]

            self.table_wdg.insertRow(i)
            self.insert_item(i, 0, "", "visibility", visible, True)
            self.insert_item(i, 1, transform_name, None, transform_name, False)
            self.insert_item(i, 2, self.float_to_string(translation[0]), "tx", translation[0], False)
            self.insert_item(i, 3, self.float_to_string(translation[1]), "ty", translation[1], False)
            self.insert_item(i, 4, self.float_to_string(translation[2]), "tz", translation[2], False)

            self.insert_item(i, 5, self.float_to_string(rotation[0]), "rx", rotation[0], False)
            self.insert_item(i, 6, self.float_to_string(rotation[1]), "ry", rotation[1], False)
            self.insert_item(i, 7, self.float_to_string(rotation[2]), "rz", rotation[2], False)

            self.insert_item(i, 8, self.float_to_string(scale[0]), "sx", scale[0], False)
            self.insert_item(i, 9, self.float_to_string(scale[1]), "sx", scale[1], False)
            self.insert_item(i, 10, self.float_to_string(scale[2]), "sx", scale[2], False)


        self.set_cell_changed_connection_enabled(True)

    def insert_item(self, row, column, text, attr, value, is_boolean):
        item = QtWidgets.QTableWidgetItem(text)
        self.set_item_attr(item, attr)
        self.set_item_value(item, value)

        if is_boolean:
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            self.set_item_checked(item, value)

        self.table_wdg.setItem(row, column, item)

    def on_cell_changed(self, row, column):
        self.set_cell_changed_connection_enabled(False)

        item = self.table_wdg.item(row, column)

        if column == 1:
            self.rename(item)
        else:
            is_boolean = column == 0
            self.update_attr(self.get_full_attr_name(row, item), item, is_boolean)

        self.set_cell_changed_connection_enabled(True)

    def rename(self, item):
        old_name = self.get_item_value(item)
        new_name = self.get_item_text(item)
        if old_name != new_name:
            actual_new_name = cmds.rename(old_name, new_name)
            if actual_new_name != new_name:
                self.set_item_text(item, actual_new_name)

            self.set_item_value(item, actual_new_name)

    def update_attr(self, attr_name, item, is_boolean):
        if is_boolean:
            value = self.is_item_checked(item)
            self.set_item_text(item, "")
        else:
            text = self.get_item_text(item)
            try:
                value = float(text)
            except ValueError:
                self.revert_original_value(item, False)
                return

        try:
            cmds.setAttr(attr_name, value)
        except:
            original_value = self.get_item_value(item)
            if is_boolean:
                self.set_item_checked(item, original_value)
            else:
                self.revert_original_value(item, False)

            return

        new_value = cmds.getAttr(attr_name)
        if is_boolean:
            self.set_item_checked(item, new_value)
        else:
            self.set_item_text(item, self.float_to_string(new_value))
        self.set_item_value(item, new_value)


    def set_item_text(self, item, text):
        item.setText(text)

    def get_item_text(self, item):
        return item.text()

    def set_item_checked(self, item, checked):
        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def is_item_checked(self, item):
        return item.checkState() == QtCore.Qt.Checked

    def set_item_attr(self, item, attr):
        item.setData(self.ATTR_ROLE, attr)

    def get_item_attr(self, item):
        return item.data(self.ATTR_ROLE)

    def set_item_value(self, item, value):
        item.setData(self.VALUE_ROLE, value)

    def get_item_value(self, item):
        return item.data(self.VALUE_ROLE)

    def get_full_attr_name(self, row, item):
        node_name = self.table_wdg.item(row, 1).data(self.VALUE_ROLE)
        attr_name = self.get_item_attr(item)
        return "{0}.{1}".format(node_name, attr_name)

    def float_to_string(self, value):
        return "{0:.4f}".format(value)

    def revert_original_value(self, item, is_boolean):
        original_value = self.get_item_value(item)
        if is_boolean:
            self.set_item_checked(item, original_value)
        else:
            self.set_item_text(item, self.float_to_string(original_value))


if __name__ == "__main__":

    try:
        transform_obj_table.close() # pylint: disable=E0601
        transform_obj_table.deleteLater()
    except:
        pass

    transform_obj_table = TransformTableDialog()
    transform_obj_table.show()
