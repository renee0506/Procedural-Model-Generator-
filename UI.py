from PySide2.QtWidgets import *
from PySide2.QtCore import *

from functools import partial

def addScaleSlider(obj, layout):
    scale = QSlider(Qt.Horizontal)
    scaleLabel = QLabel("Scale")
    scale.setMinimum(10)
    scale.setMaximum(50)
    scale.valueChanged.connect(
        partial(obj.changeScale, scale.value())
    )
    layout.addWidget(scaleLabel)
    layout.addWidget(scale)