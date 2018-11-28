#PySide2 imports
from PySide2.QtWidgets import *
from PySide2.QtCore import *

#Panda3D imports
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Point3, WindowProperties, Material, NodePath
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")

#Python Module imports
from functools import partial
import random, math
import threading, time

class Model(object):
    #Class attribute holding all models
    allModels = list()
    switcher = {
        1: "Wall",
        2: "Pole",
        3: "MainBody",
        4: "Roof",
        5: "Deco"
    }

    def __init__(self, path, model, parent):
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
        self.scale = (1,1,1)
        self.nOfSections = 20
        self.randomness = 2
        self.parent = parent
        self.showParams = True

    def __repr__(self):
        return "Model at " + self.path

    def changeMaterialColor(self, color):
        self.material.setAmbient(color)
        self.model.setMaterial(self.material)

    def changeLabel(self, dummy, index):
        self.label = Model.switcher.get(index)

    # Add Label-Specific UI
    def addLabelUI(self, dummy, layout, index):
        self.clearLayout(layout)
        scale = QSlider(Qt.Horizontal)
        scaleLabel = QLabel("Scale")
        scale.setMinimum(1)
        scale.setMaximum(10)
        scale.valueChanged.connect(
            partial(self.changeScale, scale.value())
        )
        layout.addWidget(scaleLabel)
        layout.addWidget(scale)
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
        elif Model.switcher.get(index) == "Pole": # If it is Pole
            #TODO: WRITE THE BACKEND PART OF THIS CODE
            heightLabel = QLabel("height")
            height = QSlider(Qt.Horizontal)
            height.setMinimum(1)
            height.setMaximum(10)
            height.valueChanged.connect(
                partial(self.changeHValue, height.value())
            )
            layout.addWidget(heightLabel)
            layout.addWidget(height)
        elif Model.switcher.get(index) == "MainBody":
            nOfSecLabel = QLabel("number of sections")
            nOfSec = QSlider(Qt.Horizontal)
            nOfSec.setMinimum(1)
            nOfSec.setMaximum(20)
            nOfSec.valueChanged.connect(
                partial(self.changeNofSections, nOfSec.value())
            )
            randomnessLebel = QLabel("Randomness")
            randomness = QSlider(Qt.Horizontal)
            randomness.setMinimum(1)
            randomness.setMaximum(10)
            randomness.valueChanged.connect(
                partial(self.changeRandomness, nOfSec.value())
            )
            layout.addWidget(nOfSecLabel)
            layout.addWidget(nOfSec)
        elif Model.switcher.get(index) == "Roof":
            heightLabel = QLabel("height")
            height = QSlider(Qt.Horizontal)
            height.setMinimum(1)
            height.setMaximum(10)
            height.valueChanged.connect(
                partial(self.changeHValue, height.value())
            )
            layout.addWidget(heightLabel)
            layout.addWidget(height)

        self.changeLabel(dummy, index)


    #Cited From: https://stackoverflow.com/questions/4528347/clear-all
    # -widgets-in-a-layout-in-pyqt
    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    #Read the New Width Value
    def changeWValue(self, state, w):
        self.width = round(w)
        Model.generate(self.parent)

    #Read the New Length Value
    def changeHValue(self, state, h):
        self.height = round(h)
        Model.generate(self.parent)

    #Change the scale of the model
    def changeScale(self, state, s):
        num = round(s)
        self.scale = (num, num, num)
        Model.generate(self.parent)

    # For mainBody Only, change the number of sections of the body
    def changeNofSections(self, state, sec):
        self.sections = sec
        Model.generate(self.parent)

    # For mainBody, change the randomness of height
    def changeRandomness(self, state, rand):
        self.randomness = rand
        Model.generate(self.randomness)


    @staticmethod
    def generate(scene, animated=False):
        node = scene.find("test")
        print(node)
        try:
            node.detachNode()
        except:
            print("A generation result does not exist yet")

        typeToInstances = dict()
        #Get Components from the user input
        wall = [m for m in Model.allModels if m.label == "Wall"][0]
        tower = [m for m in Model.allModels if m.label == "Pole"][0]
        mainBody = [m for m in Model.allModels if m.label == "MainBody"][0]
        roof = [m for m in Model.allModels if m.label == "Roof"][0]
        deco = [m for m in Model.allModels if m.label == "Deco"][0]

        bounds = wall.model.getTightBounds()
        minX = bounds[0][0]
        maxX = bounds[1][0]
        currentX = - (maxX - minX) * wall.width / 2
        currentY = - (maxX - minX) / 2 - (maxX - minX) * wall.height / 2
        #parent node of all wall objects
        dummy = NodePath("test")
        walls = dummy.attachNewNode("Walls")
        walls.setPos(0,0,0)

        #Generate walls on the width side
        for i in range(wall.width):
            pos = (currentX + maxX - minX, currentY + (maxX- minX) / 2, 0)
            posMirror = (currentX + maxX - minX,
                         currentY + (maxX- minX) / 2 +
                         (maxX - minX) * wall.height, 0)
            wallInstance = Instance(wall.model, walls, pos, scale = wall.scale)
            wallInstanceMirror = Instance(wall.model, walls, posMirror, scale = wall.scale)
            currentX += (maxX - minX)
            wallInstance.instantiate()
            wallInstanceMirror.instantiate()
            wallInstancies = typeToInstances.get("Walls", list())
            wallInstancies.append(wallInstance)
            wallInstancies.append(wallInstanceMirror)
            typeToInstances["Walls"] = wallInstancies

        currentX = - (maxX - minX) * wall.width / 2
        #Generate walls on the length side
        for i in range(wall.height):
            pos = (currentX + (maxX- minX) / 2, currentY + maxX - minX, 0)
            hpr = (90,0,0)
            posMirror = (currentX + (maxX- minX) / 2 +
                         (maxX - minX) * wall.width,
                        currentY + maxX - minX, 0)
            wallInstance = Instance(wall.model, walls, pos, hpr, scale = wall.scale)
            wallInstanceMirror = Instance(wall.model, walls, posMirror, hpr, scale = wall.scale)
            currentY += (maxX - minX)
            wallInstance.instantiate()
            wallInstanceMirror.instantiate()
            wallInstancies = typeToInstances.get("Walls", list())
            wallInstancies.append(wallInstance)
            wallInstancies.append(wallInstanceMirror)
            typeToInstances["Walls"] = wallInstancies

        #Hide Wall Model
        wall.model.detachNode()

        #Generate Towers
        towers = dummy.attachNewNode("Towers")
        towers.setPos(0,0,0)
        wallBounds = walls.getTightBounds()
        wallLocations = [(wallBounds[0][0], wallBounds[0][1]),
                         (wallBounds[1][0], wallBounds[0][1]),
                         (wallBounds[1][0], wallBounds[1][1]),
                         (wallBounds[0][0], wallBounds[1][1])]
        for location in wallLocations:
            pos = (location[0], location[1], 0)
            towerInstance = Instance(tower.model, towers, pos, scale = tower.scale)
            towerInstance.instantiate()
            towerInstancies = typeToInstances.get("Towers",
                                        list())
            towerInstancies.append(towerInstance)
            typeToInstances["Towers"] = towerInstancies

        #Hide Tower Model
        tower.model.detachNode()

        #Generate MainBody
        bodies = dummy.attachNewNode("Bodies")
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
        upperCorners = list()
        lowerCorners = list()
        upperCenters = list()
        surfaces = list() #for generating surface deco
        for i in range(N):
            randX = random.uniform(wallXmin + dx / 2, wallXmax - dx / 2)
            randY = random.uniform(wallYmin + dy / 2, wallYmax - dy / 2)
            randZ = random.uniform(1, mainBody.randomness)
            pos = (randX, randY, 0)
            scale = (mainBody.scale[0], mainBody.scale[1], mainBody.scale[2] * randZ)
            mainBodyInstance = Instance(mainBody.model, bodies, pos, scale=scale)
            mainBodyInstance.instantiate()
            mainBodyInstancies = typeToInstances.get("Main Body", list())
            mainBodyInstancies.append(mainBodyInstance)
            typeToInstances["Main Body"] = mainBodyInstancies

            bounds = mainBodyInstance.getTightBounds()
            min_x, min_y, min_z = bounds[0][0], bounds[0][1], \
                                  bounds[0][2]
            max_x, max_y, max_z = bounds[1][0], bounds[1][1], \
                                  bounds[1][2]
            """
                    1 --------- 6
                     | \       \
                     |  \       \
                   2 \   \ 4     \-------- 8
                      \   -------- 5
                       \  |       |
                        \ |       |
                        3 -------- 7
                    """
            point1 = (min_x, max_y, max_z)
            point2 = (min_x, min_y, min_z)
            point3 = (min_x, max_y, min_z)
            point4 = (min_x, min_y, max_z)
            point5 = (max_x, min_y, max_z)
            point6 = (max_x, max_y, max_z)
            point7 = (max_x, min_y, min_z)
            point8 = (max_x, max_y, min_z)
            fourSurfaces = [(point1, point2, point3, point4),
                            (point4, point3, point7, point5),
                            (point5, point7, point8, point6),
                            (point1, point2, point8, point6)]
            surfaces += fourSurfaces
            upperCorners.append([(min_x, min_y, max_z), (min_x, max_y, max_z),
                                 (max_x, min_y, max_z), (max_x, max_y, max_z)])
            lowerCorners.append([(min_x, min_y, min_z), (min_x, max_y, min_z),
                                 (max_x, min_y, min_z), (max_x, max_y, min_z)])
            upperCenters.append((min_x + (max_x - min_x) / 2,
                                 min_y + (max_y - min_y) / 2,
                                 max_z))
        #Hide MainBody Model
        mainBody.model.detachNode()

        roofs = dummy.attachNewNode("Bodies")
        roofs.setPos(0, 0, 0)
        #Generate Roof
        for center in upperCenters:
            pos = (center[0], center[1], center[2])
            roofInstance = Instance(roof.model, roofs, pos, scale = roof.scale)
            roofInstance.instantiate()
            roofInstancies = typeToInstances.get("Roof", list())
            roofInstancies.append(roofInstance)
            typeToInstances["Roof"] = roofInstancies
        #Hide the initial roof model
        roof.model.detachNode()

        #Generate Windows on vertical surfaces
        numberOfSurfaces = len(surfaces)
        vDecos = dummy.attachNewNode("vDecos")
        vDecos.setPos(0, 0, 0)

        for i in range(20):
            #TODO: Chage to User Input Later
            rand = random.randint(0, numberOfSurfaces)
            surface = surfaces[rand]
            randx = random.uniform(surface[1][0], surface[2][0])
            randy = random.uniform(surface[0][1], surface[1][1])
            randz = random.uniform(surface[0][2], surface[1][2])
            pos = (randx, randy, randz)
            if math.isclose(randx, surface[1][0]):
                vDecoInstance = Instance(deco.model, vDecos, pos,
                                         rotation = (0, 0, 90), scale = deco.scale)
            else:
                vDecoInstance = Instance(deco.model, vDecos, pos, scale = deco.scale)
            vDecoInstance.instantiate()
            vDecoInstancies = typeToInstances.get("Deco", list())
            vDecoInstancies.append(vDecoInstance)
            typeToInstances["Deco"] = vDecoInstancies
        deco.model.detachNode()
        castle = Castle(typeToInstances, dummy, scene)
        if not animated:
            castle.instantiate()
        elif animated:
            castle.animatedInstantiate()

#An instance of a model
class Instance(object):

    #Init an instance of a model
    def __init__(self, model, parent, location, rotation = (0,0,0),
                 scale = (1,1,1)):
        self.model = model
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.parent = parent
        self.node = None

    #Instantiate the model to this instance
    def instantiate(self):
        instance = self.parent.attachNewNode("newInstance")
        self.model.instanceTo(instance)
        instance.setPos(self.location)
        instance.setScale(self.scale)
        instance.setHpr(self.rotation)
        self.node = instance

    #Get the Tight Bounds of this instance
    def getTightBounds(self):
        if self.node is None:
            print("Object has not been instantiated yet!")
            raise Exception("Object has not been instantiated yet!")
        else:
            return self.node.getTightBounds()


#The data of the entire castle
class Castle(object):

    def __init__(self, dict, root, scene):
        self.typeToInstances = dict
        self.root = root
        self.scene = scene

    #Instances a castle to the panda3D program
    def instantiate(self):
        print(type(self.scene))
        self.root.reparentTo(self.scene)

    def animate(self):
        nodes = self.root.getChildren()
        for node in nodes:
            children = node.getChildren()
            for child in children:
                child.reparentTo(self.scene)
                time.sleep(1.0)

    #Method to generate animated process of building the structure
    def animatedInstantiate(self):
        threading.Thread(target=self.animate).start()
        print("in animated Instantiate")

    #Formate the information for output
    def format(self):
        keysRes = ""
        for key in self.typeToInstances:
            keysRes += key + "|"
        keysRes = keysRes[:-1] + "\n"
        for key in self.typeToInstances:
            keysRes += self.typeToInstances[key] + "|"
        keysRes = keysRes[:-1]
        return keysRes

    #Saves the data to the documents
    def saveCastleInfo(self):
        localtime = time.localtime(time.time())
        f = open("Saves/save" + localtime + ".txt", "r+")
        f.write(self.format())
        f.close()







