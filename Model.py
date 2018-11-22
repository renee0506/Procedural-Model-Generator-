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
import random, math
import sys

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

    #Read the New Width Value
    def changeWValue(self, state, w):
        self.width = round(w)
    #Read the New Length Value
    def changeHValue(self, state, h):
        self.height = round(h)


    @staticmethod
    def generate(scene):
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
        walls = scene.attachNewNode("Walls")
        walls.setPos(0,0,0)

        #Generate walls on the width side
        for i in range(wall.width):
            pos = (currentX + maxX - minX, currentY + (maxX- minX) / 2, 0)
            posMirror = (currentX + maxX - minX,
                         currentY + (maxX- minX) / 2 +
                         (maxX - minX) * wall.height, 0)
            wallInstance = Instance(wall.model, walls, pos)
            wallInstanceMirror = Instance(wall.model, walls, posMirror)
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
            wallInstance = Instance(wall.model, walls, pos, hpr)
            wallInstanceMirror = Instance(wall.model, walls, posMirror, hpr)
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
        towers = scene.attachNewNode("Towers")
        towers.setPos(0,0,0)
        wallBounds = walls.getTightBounds()
        wallLocations = [(wallBounds[0][0], wallBounds[0][1]),
                         (wallBounds[1][0], wallBounds[0][1]),
                         (wallBounds[1][0], wallBounds[1][1]),
                         (wallBounds[0][0], wallBounds[1][1])]
        for location in wallLocations:
            pos = (location[0], location[1], 0)
            towerInstance = Instance(tower.model, towers, pos)
            towerInstance.instantiate()
            towerInstancies = typeToInstances.get("Towers",
                                        list())
            towerInstancies.append(towerInstance)
            typeToInstances["Towers"] = towerInstancies

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
        upperCorners = list()
        lowerCorners = list()
        upperCenters = list()
        surfaces = list() #for generating surface deco
        for i in range(N):
            randX = random.uniform(wallXmin + dx / 2, wallXmax - dx / 2)
            randY = random.uniform(wallYmin + dy / 2, wallYmax - dy / 2)
            randZ = random.uniform(1, 2)
            pos = (randX, randY, 0)
            scale = (1, 1, randZ)
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

        roofs = scene.attachNewNode("Bodies")
        roofs.setPos(0, 0, 0)
        #Generate Roof
        for center in upperCenters:
            pos = (center[0], center[1], center[2])
            roofInstance = Instance(roof.model, roofs, pos)
            roofInstance.instantiate()
            roofInstancies = typeToInstances.get("Roof", list())
            roofInstancies.append(roofInstance)
            typeToInstances["Roof"] = roofInstancies
        #Hide the initial roof model
        roof.model.detachNode()

        #Generate Windows on vertical surfaces
        numberOfSurfaces = len(surfaces)
        vDecos = scene.attachNewNode("vDecos")
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
                                         rotation = (0, 0, 90))
            else:
                vDecoInstance = Instance(deco.model, vDecos, pos)
            vDecoInstance.instantiate()
            vDecoInstancies = typeToInstances.get("Deco", list())
            vDecoInstancies.append(vDecoInstance)
            typeToInstances["Deco"] = vDecoInstancies
        deco.model.detachNode()



#An instance of a model
class Instance(object):

    def __init__(self, model, parent, location, rotation = (0,0,0),
                 scale = (1,1,1)):
        self.model = model
        self.location = location
        self.rotation = rotation
        self.scale = scale
        self.scene = parent
        self.node = None

    def instantiate(self):
        instance = self.scene.attachNewNode("newInstance")
        self.model.instanceTo(instance)
        instance.setPos(self.location)
        instance.setScale(self.scale)
        instance.setHpr(self.rotation)
        self.node = instance

    def getTightBounds(self):
        if self.node is None:
            print("Object has not been instantiated yet!")
            raise Exception("Object has not been instantiated yet!")
        else:
            return self.node.getTightBounds()


#The data of the entire castle
class Castle(object):

    def __init__(self, dict):
        self.typeToInfo = dict()

    #Instances a castle to the panda3D program
    def instantiate(self):
        pass

    #Saves the data to the documents
    def saveCastleInfo(self):
        pass





