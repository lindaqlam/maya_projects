import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

class HelperMethods(object):

    @classmethod
    def retime_keys(cls, retime_value, move_to_next):
        range_start_time, range_end_time = cls.get_selected_range()
        start_keyframe_time = cls.get_start_keyframe_time(range_start_time)
        last_keyframe_time = cls.get_last_keyframe_time()
        current_time = start_keyframe_time

        new_keyframe_times = [start_keyframe_time]

        while current_time != last_keyframe_time:
            next_keyframe_time = cls.find_keyframe("next", current_time)

            if current_time < range_end_time:
                time_diff = retime_value
            else:
                time_diff = next_keyframe_time - current_time

            new_keyframe_times.append(new_keyframe_times[-1] + time_diff)
            current_time = next_keyframe_time

        if len(new_keyframe_times) > 1:
            cls.retime_keys_recursive(start_keyframe_time, 0, new_keyframe_times)

        first_keyframe_time = cls.find_keyframe("first")

        if move_to_next and range_start_time >= first_keyframe_time:
            next_keyframe_time = cls.find_keyframe("next", start_keyframe_time)
            cls.set_current_time(next_keyframe_time)
        elif range_end_time > first_keyframe_time:
            cls.set_current_time(start_keyframe_time)
        else:
            cls.set_current_time(range_start_time)

    @classmethod
    def retime_keys_recursive(cls, current_time, index, new_keyframe_times):
        if index >= len(new_keyframe_times):
            return

        updated_keyframe_time = new_keyframe_times[index]

        next_keyframe_time = cls.find_keyframe("next", current_time)

        if updated_keyframe_time < next_keyframe_time:
            cls.change_keyframe_time(current_time, updated_keyframe_time)
            cls.retime_keys_recursive(next_keyframe_time, index + 1, new_keyframe_times)
        else:
            cls.retime_keys_recursive(next_keyframe_time, index + 1, new_keyframe_times)
            cls.change_keyframe_time(current_time, updated_keyframe_time)

    @classmethod
    def set_current_time(cls, time):
        cmds.currentTime(time)

    @classmethod
    def get_selected_range(cls):
        playback_slider = mel.eval("$tempVar = $gPlayBackSlider")
        selected_range = cmds.timeControl(playback_slider, q=True, rangeArray=True)

        return selected_range

    @classmethod
    def find_keyframe(cls, which, time=None):
        kwargs = {"which": which}
        if which in ["next", "previous"]:
            kwargs["time"] = (time, time)

        return cmds.findKeyframe(**kwargs)

    @classmethod
    def change_keyframe_time(cls, current_time, new_time):
        cmds.keyframe(e=True, time=(current_time, current_time), timeChange=new_time)

    @classmethod
    def get_start_keyframe_time(cls, range_start_time):
        start_times = cmds.keyframe(q=True, time=(range_start_time, range_start_time))
        if start_times:
            return start_times[0]

        start_time = cls.find_keyframe("previous", range_start_time)
        return start_time

    @classmethod
    def get_last_keyframe_time(cls):
        return cls.find_keyframe("last")

class Retiming_Tool(QtWidgets.QDialog):

    WINDOW_TITLE = "Retiming Tool"

    @classmethod
    def maya_main_window(cls):
        """
        Return the Maya main window widget as a Python object
        """
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

    def __init__(self):
        super(Retiming_Tool, self).__init__(self.maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(300, 80)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self): #
        self.about_action = QtWidgets.QAction("Help", self)

    def create_widgets(self):
        self.menu_bar = QtWidgets.QMenuBar()
        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)

        self.label = QtWidgets.QLabel("Frames:")
        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setRange(1,50)
        self.go_btn = QtWidgets.QPushButton("Go")
        self.go_btn.setFixedWidth(50)

        self.next_frame_cb = QtWidgets.QCheckBox("Next Frame")

    def create_layouts(self):
        form_layout = QtWidgets.QHBoxLayout()
        form_layout.addStretch()
        form_layout.addWidget(self.label)
        form_layout.addWidget(self.spinbox)
        form_layout.addWidget(self.go_btn)
        form_layout.addStretch()

        next_frame_layout = QtWidgets.QHBoxLayout()
        next_frame_layout.addStretch()
        next_frame_layout.addWidget(self.next_frame_cb)
        next_frame_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(next_frame_layout)

    def create_connections(self):
        self.about_action.triggered.connect(self.about)
        
        self.go_btn.clicked.connect(self.retime)

    def retime(self):
        spin_value = self.spinbox.value()
        move_to_next = self.next_frame_cb.isChecked()

        cmds.undoInfo(openChunk=True)

        if move_to_next:
            print "True"
        else:
            print "False"

        if spin_value != 0:
            HelperMethods.retime_keys(spin_value, False, move_to_next)

    def show_context_menu(self, point):
        context_menu = QtWidgets.QMenu()
        context_menu.addAction(self.about_action)
        context_menu.exec_(self.mapToGlobal(point))

    def about(self):
            QtWidgets.QMessageBox.about(self, "About Retiming Tool", "Select an object and then specify number of desired frames between keys. Check \"Next Frame\" to automatically move to the next frame.")

if __name__ == "__main__":

    try:
        retiming_ui.close()
        retiming_ui.deleteLater()
    except:
        pass

    retiming_ui = Retiming_Tool()
    retiming_ui.show()

