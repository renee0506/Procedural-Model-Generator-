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
from functools import partial
import random
import sys

#Constants
P3D_WIN_WIDTH = 400
P3D_WIN_HEIGHT = 240

class Model(object):
    #Class attribute holding all models
    allModels = list()
    switcher = {
        1: "Wall",
        2: "Pole",
        3: "MainBody"
    }

    def __init__(self, path, model):
        self.path = path
        self.model = model
        self.label = "Wall"
        #Assign a default material
        self.model.setColor((1,0,0,1))
        self.material = Material()
        self.material.setDiffuse((1,0,0,1))
        self.model.setMaterial(self.material)
        self.model.setShaderAuto()
        self.width = 0
        self.height = 0

    def __repr__(self):
        return "Model at " + self.path

    def changeMaterialColor(self, color):
        self.material.setAmbient(color)
        self.model.setMaterial(self.material)

    def changeLabel(self, dummy, index):

        self.label = Model.switcher.get(index)

    # Add Label-Specific UI
    def addLabelUI(self, dummy, layout, index):
        if Model.switcher.get(index) == "Wall":  # If it is wall
            widthLabel = QLabel("Width")
            width = QSlider(Qt.Horizontal)
            heightLabel = QLabel("Length")
            height = QSlider(Qt.Horizontal)
            width.setMinimum(1)
            width.setMaximum(10)
            width.valueChanged.connect(
                partial(self.changeWValue, width.value()))
            height.setMinimum(1)
            height.setMaximum(10)
            height.valueChanged.connect(
                partial(self.changeHValue, height.value()))
            layout.addWidget(widthLabel)
            layout.addWidget(width)
            layout.addWidget(heightLabel)
            layout.addWidget(height)
        self.changeLabel(dummy, index)

    def changeWValue(self, state, w):
        self.width = round(w)

    def changeHValue(self, state, h):
        self.height = round(h)


    @staticmethod
    def generate(scene):
        #Get Components from the user input
        wall = [m for m in Model.allModels if m.label == "Wall"][0]
        tower = [m for m in Model.allModels if m.label == "Pole"][0]
        mainBody = [m for m in Model.allModels if m.label == "MainBody"][0]

        #print(wall.model.getTightBounds())
        bounds = wall.model.getTightBounds()
        minX = bounds[0][0]
        maxX, maxY, maxZ = bounds[1][0], bounds[1][1], bounds[1][2]
        currentX = - (maxX - minX) * wall.width / 2
        currentY = - (maxX - minX) / 2 - (maxX - minX) * wall.height / 2
        walls = scene.attachNewNode("Walls")
        walls.setPos(0,0,0)

        #Generate walls on the width side
        for i in range(wall.width):
            wallInstance = walls.attachNewNode("wall-instance")
            wallInstanceMirror = walls.attachNewNode("wall-instance-mirror")
            wallInstance.setPos(walls, currentX + maxX - minX, currentY + (maxX- minX) / 2, 0)
            wallInstanceMirror.setPos(walls, currentX + maxX - minX, currentY + (maxX- minX) / 2 + (maxX - minX) * wall.height, 0)
            currentX += (maxX - minX)
            wall.model.instanceTo(wallInstance)
            wall.model.instanceTo(wallInstanceMirror)

        currentX = - (maxX - minX) * wall.width / 2
        #Generate walls on the length side
        for i in range(wall.height):
            wallInstance = walls.attachNewNode("wall-instance")
            wallInstanceMirror = walls.attachNewNode("wall-instance-mirror")
            wallInstance.setHpr(90, 0, 0)
            wallInstance.setPos(walls, currentX + (maxX- minX) / 2, currentY + maxX - minX, 0)
            wallInstanceMirror.setPos(walls, currentX + (maxX- minX) / 2 + (maxX - minX) * wall.width,
                                      currentY + maxX - minX, 0)
            wallInstanceMirror.setHpr(90, 0, 0)
            currentY += (maxX - minX)
            wall.model.instanceTo(wallInstance)
            wall.model.instanceTo(wallInstanceMirror)
        #Hide Wall Model
        wall.model.detachNode()

        #Generate Towers
        towers = scene.attachNewNode("Towers")
        towers.setPos(0,0,0)
        wallBounds = walls.getTightBounds()
        wallLocations = [(wallBounds[0][0], wallBounds[0][1]),
                 (wallBounds[1][0], wallBounds[0][1]),
                 (wallBounds[1][0], wallBounds[1][1]),
                 (wallBounds[0][0], wallBounds[1][1])]
        for location in wallLocations:
            towerInstance = towers.attachNewNode("tower-instance")
            towerInstance.setPos(location[0], location[1], 0)
            tower.model.instanceTo(towerInstance)
        #Hide Tower Model
        tower.model.detachNode()

        #Generate MainBody
        bodies = scene.attachNewNode("Bodies")
        bodies.setPos(0,0,0)
        bodyBound = mainBody.model.getTightBounds()
        dx = bodyBound[1][0] - bodyBound[0][0]
        dy = bodyBound[1][1] - bodyBound[0][1]
        wallXmin = wallBounds[0][0]
        wallYmin = wallBounds[0][1]
        wallXmax = wallBounds[1][0]
        wallYmax = wallBounds[1][1]
        wallDx = wallXmax - wallXmin
        wallDy = wallYmax - wallYmin
        N = int(wallDx * wallDy / (dx * dy))
        for i in range(N):
            randX = random.uniform(wallXmin + dx / 2, wallXmax - dx / 2)
            randY = random.uniform(wallYmin + dy / 2, wallYmax - dy / 2)
            mainBodyInstance = bodies.attachNewNode("mainbody-instance")
            mainBodyInstance.setPos(randX, randY, 0)
            mainBody.model.instanceTo(mainBodyInstance)
        #Hide MainBody Model
        mainBody.model.detachNode()




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
        lyt = QVBoxLayout()
        addModelButton = QPushButton("Add")
        addModelButton.clicked.connect(self.addModel)
        lyt.addWidget(addModelButton)
        generateButton = QPushButton("Generate")
        generateButton.clicked.connect(partial(Model.generate, self.program.scene))
        lyt.addWidget(generateButton)
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
        vbox = QVBoxLayout()
        isWall = QComboBox()
        vbox.addWidget(isWall)
        isWall.addItems(["----", "Wall", "Pole", "Main Body"])
        isWall.currentIndexChanged.connect(partial(model.changeLabel,
                                                   isWall.currentIndex()))
        isWall.currentIndexChanged.connect(partial(model.addLabelUI,
                                                   isWall.currentIndex(),
                                                   vbox))
        selectColor = QPushButton("Select Color")
        selectColor.clicked.connect(partial(self.changeColor, model))
        vbox.addWidget(selectColor)
        groupBox.setLayout(vbox)
        self.modelLstLayout.addWidget(groupBox)

    #Popout the UI element for changing color
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

        #Disable default mouse movement
        base.disableMouse()
        # Load the ground model.
        self.scene = self.loader.loadModel("models/ground")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(5, 5, 5)
        self.scene.setPos(0, 0, 0)
        self.taskMgr.add(self.setCameraTask, "SetCameraTask")

        #Refering to the front-end
        self.window = None

        #Events
        self.accept("wheel_up", self.zoom, [0.1])
        self.accept("wheel_down", self.zoom, [-0.1])
        self.accept("q-repeat", self.rotate, [1])
        self.accept("e-repeat", self.rotate, [-1])
        self.accept("w-repeat", self.move, ["up"])
        self.accept("s-repeat", self.move, ["down"])
        self.accept("a-repeat", self.move, ["left"])
        self.accept("d-repeat", self.move, ["right"])


    #Set the initial camera position
    def setCameraTask(self, task):
        self.camera.setPos(0, -200, 220)
        self.camera.setHpr(0, -50, 0)
        self.camLens.setFocalLength(0.1)
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
        model.setScale(1,1,1)
        model.reparentTo(self.scene)
        modelObj = Model(fileName, model)
        Model.allModels.append(modelObj)
        self.window.addModelUI(modelObj)

    def fn(self, dir, num):
        print("Keyboard Input!")

    #Method to handle zoom event
    def zoom(self, dir):
        distance = base.camLens.getFocalLength()
        if distance + dir > 0.1:
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

