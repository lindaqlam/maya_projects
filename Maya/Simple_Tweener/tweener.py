from maya import cmds

def get_obj(attrs=None, selection=True):
'''
Get selected object
'''
    return cmds.ls(selection=True)[0]

def get_previous_frames(keyframes, currentTime):
'''
Get previous frame based on location of current frame
'''
    return [frame for frame in keyframes if frame < currentTime]

def get_next_frames(keyframes, currentTime):
'''
Get next frame based on location of current frame
'''
    return [frame for frame in keyframes if frame > currentTime]

def get_attr_full(obj, attr):
'''
Get all attributes of current object
'''
    return '%s.%s' % (obj, attr)

def get_all_keyframes(attrFull):
'''
Get all keyframes 
'''
    return cmds.keyframe(attrFull, query=True)

def tweenUtils(attrs, obj, currentTime, percentage):
'''
Performs actual tweening based on input values
'''
    for attr in attrs:
        attrFull = get_attr_full(obj, attr)

        keyframes = get_all_keyframes(attrFull)

        if not keyframes:
            continue

        previousKeyframes = get_previous_frames(keyframes, currentTime)

        laterKeyframes = get_next_frames(keyframes, currentTime)

        if not previousKeyframes and not laterKeyframes:
            continue

        previousFrame = max(previousKeyframes) if previousKeyframes else None
        nextFrame = min(laterKeyframes) if laterKeyframes else None

        if not previousFrame or not nextFrame:
            continue


        previousValue = cmds.getAttr(attrFull, time=previousFrame)
        nextValue = cmds.getAttr(attrFull, time=nextFrame)

        difference = nextValue-previousValue
        weightedDifference = (difference * percentage) / 100.0
        currentValue = previousValue + weightedDifference

        cmds.setKeyframe(attrFull, time=currentTime, value=currentValue)


def tween(percentage, obj=None, attrs=None, selection=True):
'''
Prepare object for tweening
'''

    if not obj and not selection:
            raise ValueError("No object given to tweet")

    if not obj:
        obj = get_obj()

    if not attrs:
        attrs = cmds.listAttr(obj, keyable=True)

    currentTime = cmds.currentTime(query=True)

    tweenUtils(attrs, obj, currentTime, percentage)

class TweenerWindow(object):
'''
This class is resposible for the interface of the tool.
'''

    windowName = "TweenerWindow"

    def show(self):
    '''
    Initialize basic UI window
    '''    
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        window = cmds.window(self.windowName, title="Object Tweener", widthHeight=(200, 400))

        self.buildUI()

        cmds.showWindow()

    def buildUI(self):
    '''
    Populate window with columns, rows, button, etc.
    '''

        column = cmds.columnLayout(adjustableColumn=False, columnAlign="left")

        cmds.rowColumnLayout( numberOfColumns=1 )
        self.tween_slider = cmds.floatSliderGrp(label='Percentage:', field=True, minValue=0.0, maxValue=100.0, fieldMinValue=0.0, fieldMaxValue=100.0, value=0, changeCommand=self.update_value)
        # first row: percentage slider

        cmds.rowColumnLayout( numberOfRows=2, rowHeight=[(1, 65), (2, 65)], rowSpacing=[(2,10)], columnSpacing=[(1, 20)] )
        cmds.iconTextButton( style='iconAndTextVertical', image='absoluteView.png', label='Graph Editor', align='center', command=self.open_graph_editor )
        cmds.iconTextButton( style='iconAndTextVertical', image='bezNormalSelect.png', label='Average', command=self.average )
        cmds.iconTextButton( style='iconAndTextVertical', image='addClip_100.png', label='Create Key', command=self.create_key )
        cmds.iconTextButton( style='iconAndTextVertical', image='deletePoint.png', label='Erase key', command=self.erase_single_key )
        cmds.iconTextButton( style='iconAndTextVertical', image='Erase.png', label='Undo', command=self.undo )
        cmds.iconTextButton( style='iconAndTextVertical', image='deleteActive.png', label='Erase keys', command=self.erase_dialog )
        cmds.iconTextButton( style='iconAndTextVertical', image='arrowLeft.png', label='Previous Key', command=self.prev_key )
        cmds.iconTextButton( style='iconAndTextVertical', image='playClip_100.png', label='Play', command=self.play )
        cmds.iconTextButton( style='iconAndTextVertical', image='arrowRight.png', label='Next Key', command=self.next_key )
        cmds.iconTextButton( style='iconAndTextVertical', image='stopClip_100.png', label='Stop', command=self.stop )
        # second row(s): all the buttons for our tool, each with an image and logo, and connected to a function

        cmds.showWindow()

        cmds.setParent( column )

    def update_value(self, *args):
    '''
    Updates tween value based on percentage slider
    '''
        self.value = cmds.floatSliderGrp(self.tween_slider, q=True, v=True)
        tween(self.value)

    def average(self, *args):
    '''
    Tweens at an "average" value generated by the left and right points
    '''
        currentTime = cmds.currentTime(query=True)
        obj = get_obj(attrs=None, selection=True)
        attrFull = get_attr_full(obj, "translateX")
        keyframes = get_all_keyframes(attrFull)

        prev_key_frame = max(get_previous_frames(keyframes, currentTime)) if keyframes else None
        next_key_frame = min(get_next_frames(keyframes, currentTime)) if keyframes else None

        if not next_key_frame:
            return

        if currentTime == prev_key_frame or currentTime == next_key_frame:
            return

        if not prev_key_frame:
            prev_key_frame = 0

        mid = prev_key_frame + (next_key_frame-prev_key_frame)/2

        cmds.currentTime( mid, edit=True )
        tween(50)

    def open_graph_editor(self, *args):
    '''
    Opens the Graph Editor
    '''
        cmds.GraphEditor()

    def undo(self, *args):
    '''
    Undoes the last command
    '''
        cmds.undo()

    def erase_single_key(self, *args):
    '''
    Erases current key
    '''
        currentTime = cmds.currentTime(query=True)
        cmds.cutKey(get_obj(), time=(currentTime, currentTime+1), attribute="translateX", option="keys")

    def erase_keys_range(self, *args):
    '''
    Erases all keys in a range
    '''
        cmds.cutKey(get_obj(), time=(self.start_time, self.end_time), attribute="translateX", option="keys")

    def create_key(self, *args):
    '''
    Creates a new key
    '''
        cmds.setKeyframe()

    def next_key(self, *args):
    '''
    Moves forward to the next key, if possible
    '''
        currentTime = cmds.currentTime(query=True)
        obj = get_obj(attrs=None, selection=True)
        attrFull = get_attr_full(obj, "translateX")
        keyframes = get_all_keyframes(attrFull)
        next_key_frame = min(get_next_frames(keyframes, currentTime)) if keyframes else None

        cmds.currentTime( next_key_frame, edit=True )

    def prev_key(self, *args):
    '''
    Moves backwards to the previous key, if possible
    '''
        currentTime = cmds.currentTime(query=True)
        obj = get_obj(attrs=None, selection=True)
        attrFull = get_attr_full(obj, "translateX")
        keyframes = get_all_keyframes(attrFull)
        prev_key_frame = max(get_previous_frames(keyframes, currentTime)) if keyframes else None

        cmds.currentTime( prev_key_frame, edit=True )

    def store_start_time(self, *args):
    '''
    Stores start time
    '''
        self.start_time = cmds.floatField(self.start, q=True, v=True)
        print self.start_time

    def store_end_time(self, *args):
    '''
    Stores end time
    '''
        self.end_time = cmds.floatField(self.end, q=True, v=True)
        print self.end_time

    def erase_dialog(self, *args):
    '''
    Shows window to specify start and end times for range delete
    '''
        window = cmds.window( title="Specify Time Range", widthHeight=(200,100))

        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label="Start Time:")
        self.start = cmds.floatField(minValue=1, maxValue=100, v=True, changeCommand=self.store_start_time)

        cmds.text(label="End Time:")
        self.end = cmds.floatField(minValue=1, maxValue=100, v=True, changeCommand=self.store_end_time)

        cmds.button(label="Erase Keys", command=self.erase_keys_range)
        cmds.showWindow(window)

    def play(self, *args):
    '''
    Plays the animation
    '''
        cmds.play(forward=True)

    def stop(self, *args):
    '''
    Stops the animation
    '''
        cmds.play( state=False )

