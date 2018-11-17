###15-112 Term Project####
###Author: Qianye(Renee) Mei

'''
The code skeleton is modified from dinoint's code from
https://discourse.panda3d.org/t/using-panda3d-with-pyqt-or-pygtk-
possible/6170
'''
#PySide2 imports
from PySide2.QtWidgets import *
from PySide2.QtCore import *

#Panda3D imports
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Point3, WindowProperties, Material
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")

#Python Module imports
from math import pi, sin, cos, sqrt
from functools import partial
import sys

#Constants
P3D_WIN_WIDTH = 400
P3D_WIN_HEIGHT = 240

class Model(object):

    def __init__(self, path, model):
        self.path = path
        self.model = model
        #Assign a default material
        self.model.setColor((1,0,0,1))
        self.material = Material()
        self.material.setDiffuse((1,0,0,1))
        self.model.setMaterial(self.material)
        self.model.setShaderAuto()

    def __repr__(self):
        return "Model at " + self.path

    def changeMaterialColor(self, color):
        self.material.setAmbient(color)
        self.model.setMaterial(self.material)

#The Main Program Window (GUI)
class QTWindow(QWidget):
    def __init__(self, program = None):
        super().__init__()

        #Refering to the backend program
        self.program = program
        #Window properties
        self.setWindowTitle("Procedural Castle Generator")
        self.setGeometry(0, 0, 800, 600)
        #Set aside the space for Panda3D window
        self.pandaContainer = QTPandaWidget(self)
        #side menu
        self.sideMenu = QWidget()
        self.menulayout = QHBoxLayout()
        #Generate initial buttons
        self.generateButtons()
        #List of Models
        self.modelLst = QWidget()
        self.modelLstLayout = QVBoxLayout()
        self.modelLst.setLayout(self.modelLstLayout)
        self.menulayout.addWidget(self.modelLst)
        self.sideMenu.setLayout(self.menulayout)

        layout = QGridLayout()
        layout.addWidget(self.pandaContainer, 0, 0)
        layout.addWidget(self.sideMenu, 0, 1, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 0)

        self.setLayout(layout)

    def generateButtons(self):
        buttonWidget = QWidget()
        lyt = QHBoxLayout()
        addModelButton = QPushButton("Add")
        addModelButton.clicked.connect(self.addModel)
        lyt.addWidget(addModelButton)
        buttonWidget.setLayout(lyt)
        self.menulayout.addWidget(buttonWidget)

    #Add Model to the Scene
    def addModel(self):
        print("In add model")
        dialog = QFileDialog(None)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
            print(fileName)
            self.program.addModel(fileName)

    #Renew the List of Models on GUI
    def addModelUI(self, model):
        groupBox = QGroupBox(model.path.split("/")[-1])
        isWall = QRadioButton("Wall")
        isWall.setChecked(False)
        vbox = QVBoxLayout()
        vbox.addWidget(isWall)
        selectColor = QPushButton("Select Color")
        selectColor.clicked.connect(partial(self.changeColor, model))
        selectColor.setStyleSheet("QWidget {background-color: %s }" %Qt.gray)
        vbox.addWidget(selectColor)
        groupBox.setLayout(vbox)
        self.modelLstLayout.addWidget(groupBox)

    def changeColor(self, m):
        picker = QColorDialog()
        if picker.exec_():
            color = picker.selectedColor().getRgbF()
            print(color)
            m.model.setColor(color)


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

        #Refering to the front-end
        self.window = None

        #Events
        self.accept("wheel_up", self.zoom, [1])
        self.accept("wheel_down", self.zoom, [-1])
        self.accept("q-repeat", self.rotate, [1])
        self.accept("e-repeat", self.rotate, [-1])
        self.accept("w-repeat", self.move, ["up"])
        self.accept("s-repeat", self.move, ["down"])
        self.accept("a-repeat", self.move, ["left"])
        self.accept("d-repeat", self.move, ["right"])


    #Set the initial camera position
    def setCameraTask(self, task):
        self.camera.setPos(50, -50, 90)
        self.camera.setHpr(45, -50, 0)
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
        model = self.loader.loadModel(fileName)
        model.setPos(0, 0, 0)
        model.setScale(2,2,2)
        model.reparentTo(self.scene)
        modelObj = Model(fileName, model)
        self.models.add(modelObj)
        self.window.addModelUI(modelObj)

    def fn(self, dir, num):
        print("Keyboard Input!")

    #Method to handle zoom event
    def zoom(self, dir):
        distance = base.camLens.getFocalLength()
        if distance + dir > 0:
            base.camLens.setFocalLength(distance + dir)

    #Method to rotate the scene
    def rotate(self, dir):
        self.scene.setH(self.scene.getH() + 5 * dir)

    #Method to move around
    def move(self, dir):
        print("In Move")
        pos = self.camera.getPos()
        if dir == "up":
            self.camera.setPos(pos[0], pos[1] + 1, pos[2])
        elif dir == "down":
            self.camera.setPos(pos[0], pos[1] - 1, pos[2])
        elif dir == "left":
            self.camera.setPos(pos[0] - 1, pos[1], pos[2])
        else:
            self.camera.setPos(pos[0] + 1, pos[1], pos[2])


if __name__ == '__main__':
    world = World()
    app = QApplication(sys.argv)
    form = QTWindow(world)
    world.window = form
    world.bindToWindow(int(form.winId()))
    form.show()
    world.run()
    app.exec_()

