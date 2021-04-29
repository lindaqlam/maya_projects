import maya.cmds as cmds
import maya.OpenMaya as om
import random as random

class WireframeColors(object):
''' 
This class is responsible for the functionality of our tool
'''

    @classmethod
    def set_color(cls, color_values):

        selection = cmds.ls(selection=True)

        for obj in selection:
            try:
                cmds.color( obj, rgb=(color_values[0], color_values[1], color_values[2]) )
                # set wireframe color to the color_values passed in
            except:
                om.MGlobal.displayWarning("Failed to override color: {0}".format(obj))

        if not selection:
            om.MGlobal.displayError("No shape nodes selected")
            return False

        return True

    @classmethod
    def set_random_colors(cls):

        selection = cmds.ls(selection=True)

        for obj in selection:
            color = cls.random_color()
            # generate a random color for each object

            try:
                cmds.color( obj, rgb=(color[0], color[1], color[2]) )
                # try setting that color
                # color stores a list of 3 values (RGB)
            except:
                om.MGlobal.displayWarning("Could not set wireframe color for: {0}".format(obj))

        if not selection:
            om.MGlobal.displayError("No objects selected")
            return False

        return True


    @classmethod
    def default(cls):
        selection = cmds.ls(selection=True)

        if not selection:
            om.MGlobal.displayError("No objects selected")
            return False

        for obj in selection:
            try:
                cmds.color(obj)
                # change color to default color 
                print obj
            except:
                om.MGlobal.displayWarning("Could not reset wireframe color of {0}".format(obj))

        return True

    @classmethod
    def random_color(self, *args):
        colors = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
        # generating 3 random RGB values
        return colors


class WireframeColorsUi(object):
'''
This class is responsible for the UI of our tool
'''

    WINDOW_NAME = "WireframeColorsTool"

    def display(self):
        self.delete() # if there is a window already open, delete first before reopening a new one (ensures multiple windows aren't open at once)
        self.main_window = cmds.window(self.WINDOW_NAME, title="Set Wireframe Colors", widthHeight=(200, 150), sizeable=True) 
        # initializing our window

        self.buildUI()

    def buildUI(self):
        column_layout = cmds.rowColumnLayout( parent=self.main_window, numberOfColumns=1, columnWidth=(1,250))
        cmds.iconTextButton(style='iconAndTextVertical', image="colorPresetSpectrum.png", label="Select Color", height=50, command=self.open_color_editor)
        cmds.iconTextButton(style='iconAndTextVertical', image="undo.png", label="Undo", height=50, command=self.undo)
        cmds.iconTextButton(style='iconAndTextVertical', image="colorPickCursor.png", label="Set One Random Color", height=50, command=self.single_random_color_action)
        cmds.iconTextButton(style='iconAndTextVertical', image="colorProfile.png", label="Set All Random Colors", height=50, command=self.all_random_colors_action)
        cmds.iconTextButton(style='iconAndTextVertical', image="Erase.png", label="Reset", height=50, command=self.reset)
        # create buttons in the layout and connect them to functions


        cmds.showWindow(self.main_window)

    def open_color_editor(self, *args):
        cmds.colorEditor(parent=self.main_window)
        self.color_values = cmds.colorEditor(query=True, rgb=True)

        WireframeColors().set_color(self.color_values)

    def undo(self, *args):
        cmds.undo()
        # undoes the last command

    def single_random_color_action(self, *args):
        WireframeColors().set_color(WireframeColors().random_color())
        # set a wireframe to a specific color

    def all_random_colors_action(self, *args):
        WireframeColors().set_random_colors()
        # assign random colors to all wireframes

    def reset(self, *args):
        WireframeColors().default()
        # reset the wireframe colors to the default color

    def delete(cls):
        if cmds.window(cls.WINDOW_NAME, exists=True):
            cmds.deleteUI(cls.WINDOW_NAME, window=True)
        # if a window is currently opened, close it



if __name__ == "__main__":
    WireframeColorsUi.display()
