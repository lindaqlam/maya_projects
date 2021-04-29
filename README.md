# Simple Maya Tool Projects

A few simple tools I've built in Autodesk Maya using Python, Qt, Pyside, and the Maya cmds library.  (I'm still figuring out how to organize this repo but currently it is a place to store and keep track of my Maya projects!)

### 1. [Object Transformer Utility]()
- (My first full project in Maya) This simple tool keeps track of all the objects within the scene and allows users an easy way to toggle their visibility as well as modify transform attributes.

### 2. [Object Renamer]()
- This tool lets users quickly rename one or many objects at once, depending on what is selected in the scene. Users can also add a prefix and/or suffix, and find and replace certain values in existing names.

### 3. [Scene & Asset Utility Tool]()
- For quick saving and/or importing of objects and entire scenes. Users have the option of specifying the name to be saved as, the location to be saved at, and the file format to be saved in.

### 4. [Retiming Tool]()
- A simple shelf tool for changing the timing and spacing of an animation, utilizing a spinbox for specifcing number of frames to insert.

### 5. [Animation Tweener]()
- Based by some real tweeners I've come across online (including Dhruv Govil's), my version of a basic tweener lets users select tweening percentages, insert keys exactly in the middle of two existing keys, erase one or multiple keys in a specified range, and navigate easily between keys. My tool UI also contains quick access to the graph editor, undo button, and the play and stop buttons for animation.

### 6. [Wireframe Color Tool]()
- An imitation of Maya's existing Wireframe Color Setter tool that allows users to change the color of one or more object wireframes by selecting a color(s) from the color editor. My version comes with an additional feature of generating random colors for one or more wireframes. Other features include quick undo and reseting to the default color.
