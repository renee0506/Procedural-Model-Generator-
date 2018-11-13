###15-112 Term Project####
###Author: Qianye(Renee) Mei

'''
The starter code is modified from dinoint's code from
https://discourse.panda3d.org/t/using-panda3d-with-pyqt-or-pygtk-
possible/6170
'''
#PySide2 imports
from PySide2.QtWidgets import *
from PySide2.QtCore import *
#from PySide2.QtCore.QtObject import *

#Panda3D imports
#import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, WindowProperties

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")

#Python Module imports
from math import pi, sin, cos
import sys

#Constants
P3D_WIN_WIDTH = 400
P3D_WIN_HEIGHT = 240

class Model(object):

    def __init__(self, path):
        self.path = path

#The Main Program Window
class QTWindow(QWidget):
    def __init__(self, program = None):
        super().__init__()
        self.program = program
        self.setWindowTitle("Procedural Castle Generator")
        self.setGeometry(0, 0, 400, 300)

        self.pandaContainer = QTPandaWidget(self)

        self.sideMenu = QWidget()

        self.generateButtons()

        layout = QGridLayout()
        layout.addWidget(self.pandaContainer, 0, 0)
        layout.addWidget(self.sideMenu, 0, 1, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 0)

        self.setLayout(layout)

    def generateButtons(self):
        layout = QVBoxLayout()
        addModelButton = QPushButton("Add")
        addModelButton.clicked.connect(self.addModel)
        layout.addWidget(addModelButton)
        self.sideMenu.setLayout(layout)

    #Add Model to the Scene
    def addModel(self):
        print("In add model")
        dialog = QFileDialog(None)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
            print(fileName)
            self.program.addModel(fileName)



#The resizable widget holding the panda3D window
class QTPandaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def resizeEvent(self, evt):
        wp = WindowProperties()
        wp.setSize(self.width(), self.height())
        wp.setOrigin(self.x(), self.y())
        base.win.requestProperties(wp)

    def minimumSizeHint(self):
        return QSize(400, 300)

#ShowBase from panda3D
class World(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.models = set()

        #Disable default mouse movement
        base.disableMouse()
        # Load the ground model.
        self.scene = self.loader.loadModel("models/ground")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(2, 2, 2)
        self.scene.setPos(0, 0, 0)
        self.taskMgr.add(self.setCameraTask, "SetCameraTask")

    #Set the initial camera position
    def setCameraTask(self, task):
        self.camera.setPos(0, -15, 70)
        self.camera.setHpr(0, -80, 0)
        return Task.done


    def bindToWindow(self, windowHandle):
        wp = WindowProperties().getDefault()
        wp.setOrigin(0, 0)
        wp.setSize(P3D_WIN_WIDTH, P3D_WIN_HEIGHT)
        wp.setParentWindow(windowHandle)
        self.wp = wp
        base.openDefaultWindow(props=wp)

    def addModel(self, fileName):
        print("in add Model in ShowBase")
        self.models.add(Model(fileName))
        model = self.loader.loadModel(fileName)
        model.reparentTo(self.render)
        model.setPos(-8, 42, 0)
        model.setScale(2,2,2)




if __name__ == '__main__':
    world = World()

    app = QApplication(sys.argv)
    form = QTWindow(world)
    world.bindToWindow(int(form.winId()))
    form.show()
    world.run()
    app.exec_()

