#PySide2 imports
from PySide2.QtWidgets import *
from PySide2.QtCore import *

#Panda3D imports
from panda3d.core import Point3, WindowProperties, Material, NodePath,\
                        GeomNode
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")

#Python Module imports
from functools import partial
import random, math
import threading, time
import json

from Geometry import *

class Model(object):
    #Class attribute holding all models
    allModels = list()
    switcher = {
        1: "Wall",
        2: "Tower",
        3: "MainBody",
        4: "Roof"
    }
    showBase = None

    def __init__(self, path, model, parent):
        self.path = path
        self.model = model
        self.label = "Wall"
        #Assign a default material
        self.model.setColor((1,0,0,1))
        self.material = Material()
        self.material.setShininess(0.0)
        self.material.setAmbient((0.2,0,0,1))
        self.material.setDiffuse((0.5,0,0,1))
        self.model.setMaterial(self.material)
        self.model.setShaderAuto()
        self.width = 1
        self.length = 1
        self.height = 1
        self.scale = (1,1,1)
        self.nOfSections = 20
        self.randomness = 20
        self.color = (1,0,0,1)
        self.parent = parent.scene
        self.showParams = True

    def __repr__(self):
        return "Model at " + self.path

    def changeMaterialColor(self, color):
        self.color = color
        self.material.setDiffuse(color)
        self.model.setMaterial(self.material)

    def changeLabel(self, dummy, index):
        self.label = Model.switcher.get(index)

    # Add Label-Specific UI
    def addLabelUI(self, dummy, layout, index):
        Model.clearLayout(layout)
        scale = QSlider(Qt.Horizontal)
        scaleLabel = QLabel("Scale")
        scale.setMinimum(10)
        scale.setMaximum(50)
        scale.valueChanged.connect(
            partial(self.changeScale, scale.value())
        )
        layout.addWidget(scaleLabel)
        layout.addWidget(scale)
        if Model.switcher.get(index) == "Wall":  # If it is wall
            widthLabel = QLabel("Width")
            width = QSlider(Qt.Horizontal)
            lengthLabel = QLabel("Length")
            length = QSlider(Qt.Horizontal)
            width.setMinimum(1)
            width.setMaximum(10)
            width.valueChanged.connect(
                partial(self.changeWValue, width.value()))
            length.setMinimum(1)
            length.setMaximum(10)
            length.valueChanged.connect(
                partial(self.changeLValue, length.value()))
            heightLabel = QLabel("Height")
            height = QSlider(Qt.Horizontal)
            height.setMinimum(10)
            height.setMaximum(100)
            height.valueChanged.connect(
                partial(self.changeHValue, height.value())
            )
            layout.addWidget(heightLabel)
            layout.addWidget(height)
            layout.addWidget(widthLabel)
            layout.addWidget(width)
            layout.addWidget(lengthLabel)
            layout.addWidget(length)
        elif Model.switcher.get(index) == "Tower": # If it is Pole
            #TODO: WRITE THE BACKEND PART OF THIS CODE
            heightLabel = QLabel("Height")
            height = QSlider(Qt.Horizontal)
            height.setMinimum(10)
            height.setMaximum(100)
            height.valueChanged.connect(
                partial(self.changeHValue, height.value())
            )
            layout.addWidget(heightLabel)
            layout.addWidget(height)
        elif Model.switcher.get(index) == "MainBody":
            heightLabel = QLabel("Height")
            height = QSlider(Qt.Horizontal)
            height.setMinimum(10)
            height.setMaximum(100)
            height.valueChanged.connect(
                partial(self.changeHValue, height.value())
            )
            layout.addWidget(heightLabel)
            layout.addWidget(height)
            randomnessLabel = QLabel("Height Randomness")
            randomness = QSlider(Qt.Horizontal)
            randomness.setMinimum(10)
            randomness.setMaximum(100)
            randomness.valueChanged.connect(
                partial(self.changeRandomness, randomness.value())
            )
            layout.addWidget(randomnessLabel)
            layout.addWidget(randomness)
        elif Model.switcher.get(index) == "Roof":
            pass

        self.changeLabel(dummy, index)

    # Cited From: https://stackoverflow.com/questions/4528347/clear-all
    # -widgets-in-a-layout-in-pyqt
    @staticmethod
    def clearLayout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    #Read the New Width Value
    def changeWValue(self, state, w):
        self.width = round(w)
        Model.generate(self.parent)

    # Read the New Width Value
    def changeLValue(self, state, l):
        self.length = round(l)
        Model.generate(self.parent)

    #Read the New Length Value
    def changeHValue(self, state, h):
        self.height = h /10.0
        Model.generate(self.parent)

    #Change the scale of the model
    def changeScale(self, state, s):
        s = s / 10.0
        self.scale = (s, s, s)
        Model.generate(self.parent)

    # For mainBody Only, change the number of sections of the body
    def changeNofSections(self, state, sec):
        self.sections = sec
        Model.generate(self.parent)

    # For mainBody, change the randomness of height
    def changeRandomness(self, state, rand):
        self.randomness = rand / 10.0
        Model.generate(self.parent)


    @staticmethod
    def generate(scene, animated=False):
        node = scene.find("test")
        try:
            node.detachNode()
        except:
            print("A generation result does not exist yet")

        typeToInstances = dict()
        #Get Components from the user input
        try:
            wall = [m for m in Model.allModels if m.label == "Wall"][0]
            tower = [m for m in Model.allModels if m.label == "Tower"][0]
            mainBody = [m for m in Model.allModels if m.label == "MainBody"][0]
            roof = [m for m in Model.allModels if m.label == "Roof"][0]
        except:
            print("Please Add All Components to the Scene First!")
            return

        bounds = wall.model.getTightBounds()
        minX = bounds[0][0]
        maxX = bounds[1][0]
        currentX = - (maxX - minX) * wall.scale[0] * wall.width / 2
        currentY = - (maxX - minX) * wall.scale[0] / 2 - (maxX - minX) * wall.scale[0] * wall.length / 2
        #parent node of all wall objects
        dummy = NodePath("test")
        walls = dummy.attachNewNode("Walls")
        walls.setPos(0,0,0)

        #Generate walls on the width side
        for i in range(wall.width):
            pos = (currentX + (maxX - minX) * wall.scale[0], currentY + (maxX- minX) * wall.scale[0] / 2, 0)
            posMirror = (currentX + (maxX - minX) * wall.scale[0],
                         currentY + (maxX- minX) * wall.scale[0] / 2 +
                         (maxX - minX) * wall.scale[0] * wall.length, 0)
            scale = (wall.scale[0], wall.scale[1], wall.scale[2] * wall.height)
            wallInstance = Instance(wall.model, walls, pos, scale = scale)
            wallInstanceMirror = Instance(wall.model, walls, posMirror, scale = scale)
            currentX += (maxX - minX) * wall.scale[0]
            wallInstance.instantiate()
            wallInstanceMirror.instantiate()
            wallInstancies = typeToInstances.get("Wall", list())
            wallInstancies.append(wallInstance)
            wallInstancies.append(wallInstanceMirror)
            typeToInstances["Wall"] = wallInstancies

        currentX = - (maxX - minX) * wall.scale[0] * wall.width / 2
        #Generate walls on the length side
        for i in range(wall.length):
            pos = (currentX + (maxX- minX) * wall.scale[0] / 2, currentY + (maxX - minX) * wall.scale[0], 0)
            hpr = (90,0,0)
            posMirror = (currentX + (maxX- minX) * wall.scale[0] / 2 +
                         (maxX - minX) * wall.scale[0] * wall.width,
                        currentY + (maxX - minX) * wall.scale[0], 0)
            scale = (wall.scale[0], wall.scale[1], wall.scale[2] * wall.height)
            wallInstance = Instance(wall.model, walls, pos, hpr, scale = scale)
            wallInstanceMirror = Instance(wall.model, walls, posMirror, hpr, scale = scale)
            currentY += (maxX - minX) * wall.scale[0]
            wallInstance.instantiate()
            wallInstanceMirror.instantiate()
            wallInstancies = typeToInstances.get("Wall", list())
            wallInstancies.append(wallInstance)
            wallInstancies.append(wallInstanceMirror)
            typeToInstances["Wall"] = wallInstancies

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
            scale = (tower.scale[0], tower.scale[1], tower.scale[2] * tower.height)
            towerInstance = Instance(tower.model, towers, pos, scale=scale)
            towerInstance.instantiate()
            towerInstancies = typeToInstances.get("Tower",
                                        list())
            towerInstancies.append(towerInstance)
            typeToInstances["Tower"] = towerInstancies

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
        N = int(wallDx * wallDy / (dx * mainBody.scale[0] * dy * mainBody.scale[0]))
        upperCenters = list()
        mainBodyBounds = []#For the use of generating floor plan later
        for i in range(N):
            randX = random.uniform(wallXmin + dx / 2, wallXmax - dx / 2)
            randY = random.uniform(wallYmin + dy / 2, wallYmax - dy / 2)
            randZ = random.uniform(0, mainBody.randomness)
            pos = (randX, randY, 0)
            scale = (mainBody.scale[0], mainBody.scale[1],
                     mainBody.scale[2] * mainBody.height * (1 - 0.1 * randZ))
            mainBodyInstance = Instance(mainBody.model, bodies, pos, scale = scale)
            mainBodyInstance.instantiate()
            mainBodyInstancies = typeToInstances.get("MainBody", list())
            mainBodyInstancies.append(mainBodyInstance)
            typeToInstances["MainBody"] = mainBodyInstancies

            bounds = mainBodyInstance.getTightBounds()
            min_x, min_y, min_z = bounds[0][0], bounds[0][1], \
                                  bounds[0][2]
            max_x, max_y, max_z = bounds[1][0], bounds[1][1], \
                                  bounds[1][2]
            upperCenters.append((min_x + (max_x - min_x) / 2,
                                 min_y + (max_y - min_y) / 2,
                                 max_z))
            mainBodyBounds.append(bounds)
        #Hide MainBody Model
        mainBody.model.detachNode()

        roofs = dummy.attachNewNode("Roofs")
        roofs.setPos(0, 0, 0)
        #Generate Roof
        for center in upperCenters:
            pos = (center[0], center[1], center[2])
            scale = (roof.scale[0], roof.scale[1],
                     roof.scale[2] * roof.height)
            roofInstance = Instance(roof.model, roofs, pos, scale = scale)
            roofInstance.instantiate()
            roofInstancies = typeToInstances.get("Roof", list())
            roofInstancies.append(roofInstance)
            typeToInstances["Roof"] = roofInstancies
        #Hide the initial roof model
        roof.model.detachNode()

        #Floor Plan
        floors = dummy.attachNewNode("Floors")
        for i in range(0, 2 * len(mainBodyBounds)):
            bound = random.choices(mainBodyBounds)
            z = random.uniform(bounds[0][2], bounds[1][2])
            x1 = bounds[0][0]
            x2 = bounds[1][0]
            y1 = bounds[0][1]
            y2 = bounds[1][1]
            floor = makeSquare(x1, y1, z, x2, y2, z)
            floorNode = GeomNode("floor")
            floorNode.addGeom(floor)
            floors.attachNewNode(floorNode)

        castle = Castle(typeToInstances, dummy, scene)
        Model.showBase.castle = castle
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
        instance.setHpr(self.rotation)
        instance.setScale(self.scale[0], self.scale[1], self.scale[2])
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

    def __init__(self, dict, root, scene, program = None):
        self.typeToInstances = dict
        self.root = root
        self.scene = scene
        self.program = program

    #Instances a castle to the panda3D program
    def instantiate(self):
        self.root.reparentTo(self.scene)

    def animate(self):
        nodes = self.root.getChildren()
        test = self.scene.attachNewNode("test")
        for node in nodes:
            children = node.getChildren()
            for child in children:
                child.reparentTo(test)
                time.sleep(0.2)

    #Method to generate animated process of building the structure
    def animatedInstantiate(self):
        threading.Thread(target=self.animate).start()
        print("in animated Instantiate")

    #Formate the information for output
    def format(self):
        lst = {}
        for key in self.typeToInstances:
            instances = self.typeToInstances[key]
            print(key)
            lst[key] = {
                "model": [m for m in Model.allModels if m.label == key][0].path,
                "color":[m for m in Model.allModels if m.label == key][0].color,
                "locations": [instance.location for instance in instances],
                "scale": [instance.scale for instance in instances],
                "rotation": [instance.rotation for instance in instances]
            }
        formated = json.dumps(lst)
        return formated

    #Saves the data to the documents
    def saveCastleInfo(self):
        localtime = time.localtime(time.time())
        f = open("Saves/save" + str(localtime.tm_year) + ":" +
                 str(localtime.tm_mon) + ":" + str(localtime.tm_hour) + ":" +
                 str(localtime.tm_min) + ".txt", "w+")
        f.write(self.format())
        f.close()

    #Load Castle Data
    def load(self, data):
        print(json.loads(data))

    def generateFromLoadData(self):
        pass







