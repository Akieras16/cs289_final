import numpy as np
import math
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QDateTime, Qt, QTimer, QPoint, QRect, QPropertyAnimation, QParallelAnimationGroup
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView)
from PyQt5.QtGui import QDoubleValidator, QColor, QPen, QPainter, QBrush, QPolygonF
import pyqtgraph as pg 
import sys
from graphicsview import SceneState
from time import sleep
from tqdm import tqdm

class MenuController(QDialog):
	def __init__(self, parent=None):
		super(MenuController, self).__init__(parent)

		self.c = 0
		self.backgroundColor = QColor(38, 44, 105)
		self.cellColor = QColor(209, 220, 237)
		self.woundColor = QColor(252, 236, 0)
		self.woundPen = QPen(self.woundColor)
		self.woundPen.setWidth(3)
		self.foregroundBrush = QBrush()
		self.woundGraphics = None

		self.sceneState = SceneState()
		self.originalPalette = QApplication.palette()

		settingsComboBox = QComboBox()
		settingsComboBox.addItems(QStyleFactory.keys())

		mainLabel = QLabel("Simulation Controls")
		mainLabel.setBuddy(settingsComboBox)

		self.createWoundControlBox()
		self.createSimulationControlBox()
		self.createGraphicsDisplay()

		mainLayout = QGridLayout()
		mainLayout.addWidget(self.graphicsDisplayBox, 0, 0, 2, 10)
		mainLayout.addWidget(self.woundControlBox, 0, 11)
		mainLayout.addWidget(self.simulationControlBox, 1, 11)
		self.setLayout(mainLayout)

		self.setWindowTitle("WoundSimulation")
		self.simRunning = False

	def setWoundTrue(self):
		self.sceneState.setWound(True)
		self.drawWound()

	def setWoundFalse(self):
		if(self.woundGraphics):
			self.graphicsScene.removeItem(self.woundGraphics)
			self.woundGraphics = None

			for c in self.sceneState.visible_cells:
				self.sceneState.removeCellGraphics(c, self.graphicsScene)

			self.foregroundBrush.setColor(self.cellColor)
			self.foregroundBrush.setStyle(Qt.SolidPattern)

			for c in self.sceneState.cells:
				self.sceneState.addCellGraphics(c, self.graphicsScene)
			self.sceneState.update_cell_info()
		self.sceneState.setWound(False)

	def toggleArea(self):
		self.sceneState.setArea(float(self.woundArea.text()))

	def toggleAngles(self):
		self.sceneState.setAngles(int(self.angleEditor.value()))

	def setLine(self):
		self.sceneState.setGeometry("line")

	def setPoly(self):
		self.sceneState.setGeometry("poly")

	def setCircle(self):
		self.sceneState.setGeometry("circle")

	def removeCells(self, cells):
		
		for c in cells:
			i = self.cellGraphicsItems.index(c)
			del self.sceneState.cells[i]

			self.removeCellGraphics(c)

	def cleanupCells(self):
		for cell in self.sceneState.cells:
			if cell.collidesWithItem(self.woundGraphics):
				self.sceneState.removeCellGraphics(cell, self.graphicsScene)
	
	def clearSceneOfGraphics(self):
		for cell in self.sceneState.visible_cells:
			self.sceneState.removeCellGraphics(cell, self.graphicsScene)

		self.graphicsScene.removeItem(self.woundGraphics)
		self.woundGraphics = None

	def setPenToCells(self):
		self.foregroundBrush.setColor(self.cellColor)
		self.foregroundBrush.setStyle(Qt.SolidPattern)

	def drawWound(self):
		print("DRAWING WOUND\n")
		if(self.woundGraphics):
			self.graphicsScene.removeItem(self.woundGraphics)
			self.woundGraphics = None

		for cell in self.sceneState.visible_cells:
			self.sceneState.removeCellGraphics(cell, self.graphicsScene)

		self.setPenToCells()
		
		for cell in self.sceneState.cells:
			self.sceneState.addCellGraphics(cell, self.graphicsScene)

		geo = self.sceneState.getGeometry()
		area = self.sceneState.getArea()
		angles = self.sceneState.getAngles()
		self.foregroundBrush.setColor(self.woundColor)
		
		if(geo == "line"):
			self.woundGraphics = self.graphicsScene.addRect(0, 256 - area/2, 512, area, self.woundPen)
		elif(geo == "poly"):
			r = math.sqrt(area / (math.pi))
			poly = QPolygonF()
			for i in range(1, angles + 1):
				px, py = (r * math.cos(2 * math.pi * i / angles), r * math.sin(2 * math.pi * i / angles))
				p = QPoint(px + 256, py + 256)
				poly.append(p)
			self.woundGraphics = self.graphicsScene.addPolygon(poly, self.woundPen)
		elif(geo == "circle"):
			r = math.sqrt(area / (math.pi))
			self.woundGraphics = self.graphicsScene.addEllipse(256 - (r/2), 256 - (r/2), r, r, self.woundPen)

		self.cleanupCells()


	def createWoundControlBox(self):
		self.woundControlBox = QGroupBox("Wound")

		checkBox = QCheckBox("Add Wound")
		checkBox.setTristate(False)
		checkBox.setChecked(False)


		layout = QVBoxLayout()

		self.woundArea = QLineEdit()

		horizbox = QHBoxLayout()

		geometryLine = QRadioButton("Line")
		geometryPolygon = QRadioButton("Polygon")
		geometryCircle = QRadioButton("Circle")
		geometryLine.setChecked(True)
		geometryLine.clicked.connect(self.setLine)
		geometryPolygon.clicked.connect(self.setPoly)
		geometryCircle.clicked.connect(self.setCircle)
		horizbox.addWidget(geometryLine, 0)
		horizbox.addWidget(geometryPolygon, 1)
		horizbox.addWidget(geometryCircle, 2)

		areaValidator = QDoubleValidator()
		areaValidator.setBottom(50.0)
		areaValidator.setTop(100000.0)
		self.woundArea.setValidator(areaValidator)
		self.woundArea.editingFinished.connect(self.toggleArea)

		# create wound angle editor widget
		self.angleEditor = QSlider(Qt.Horizontal)
		self.angleEditor.setMinimum(3)
		self.angleEditor.setMaximum(50)
		self.angleEditor.setSingleStep(1)
		self.angleEditor.setValue(1)
		self.angleEditor.setTickInterval(10)
		self.angleEditor.setTickPosition(QSlider.TicksBelow)
		self.angleEditor.sliderReleased.connect(self.toggleAngles)

		addWound = QPushButton('Add Wound')
		removeWound = QPushButton('Remove Wound')
		addWound.clicked.connect(self.setWoundTrue)
		removeWound.clicked.connect(self.setWoundFalse)

		self.cellGraphicsItems = list()

		layout.addWidget(self.woundArea, 0)
		layout.addLayout(horizbox)
		layout.addWidget(self.angleEditor, 1)
		layout.addWidget(addWound)
		layout.addWidget(removeWound)
		self.woundControlBox.setLayout(layout)

	def toggleRadioOne(self):
		self.sceneState.setTimeFactor(0.5)

	def toggleRadioTwo(self):
		self.sceneState.setTimeFactor(1.0)

	def toggleRadioThree(self):
		self.sceneState.setTimeFactor(1.5)

	def toggleRadioFour(self):
		self.sceneState.setTimeFactor(2.0)

	def toggleRadioFive(self):
		self.sceneState.setTimeFactor(5.0)

	def toggleRadioSix(self):
		self.sceneState.setTimeFactor(10.0)

	def startSim(self):
		self.simRunning = True
		self.runSimulation()

	def pauseSim(self):
		print("Pausing sim\n")
		self.timer.stop()

	def changeR1Coeff(self):
		self.sceneState.setR1(float(self.r1coeffedit.text()))

	def changeR2Coeff(self):
		self.sceneState.setR2(float(self.r2coeffedit.text()))

	def changeR3Coeff(self):
		self.sceneState.setR3(float(self.r3coeffedit.text()))

	def createSimulationControlBox(self):
		self.simulationControlBox = QGroupBox("Simulation")

		# create editors for rule coefficients
		r1coefflabel = QLabel("Rule 1 Coefficient")
		self.r1coeffedit = QLineEdit()

		r2coefflabel = QLabel("Rule 2 Coefficient")
		self.r2coeffedit = QLineEdit()

		r3coefflabel = QLabel("Rule 3 Coefficient")
		self.r3coeffedit = QLineEdit()

		self.r1coeffedit.setPlaceholderText("0.01")
		self.r2coeffedit.setPlaceholderText("0.01")
		self.r3coeffedit.setPlaceholderText("0.01")


		# create validators for rule coefficient editors
		r1Validator = QDoubleValidator()
		r1Validator.setBottom(-1.1)
		r1Validator.setTop(1.1)

		r2Validator = QDoubleValidator()
		r2Validator.setBottom(-1.1)
		r2Validator.setTop(1.1)

		r3Validator = QDoubleValidator()
		r3Validator.setBottom(-1.1)
		r3Validator.setTop(1.1)

		self.r1coeffedit.setValidator(r1Validator)
		self.r2coeffedit.setValidator(r2Validator)
		self.r3coeffedit.setValidator(r3Validator)

		self.r1coeffedit.editingFinished.connect(self.changeR1Coeff)
		self.r2coeffedit.editingFinished.connect(self.changeR2Coeff)
		self.r3coeffedit.editingFinished.connect(self.changeR3Coeff)

		
		#self.woundArea.editingFinished.connect(self.toggleArea)
		
		#self.simulationControlBox = QGroupBox("Simulation")

		timeLabel = QLabel('Simulation Speed')
		radioButton1 = QRadioButton("0.5x Speed")
		radioButton2 = QRadioButton("1.0x Speed")
		radioButton3 = QRadioButton("1.5x Speed")
		radioButton4 = QRadioButton("2.0x Speed")
		radioButton5 = QRadioButton("5.0x Speed")
		radioButton6 = QRadioButton("10.0x Speed")
		radioButton2.setChecked(True)

		radioButton1.clicked.connect(self.toggleRadioOne)
		radioButton2.clicked.connect(self.toggleRadioTwo)
		radioButton3.clicked.connect(self.toggleRadioThree)
		radioButton4.clicked.connect(self.toggleRadioFour)
		radioButton5.clicked.connect(self.toggleRadioFive)
		radioButton6.clicked.connect(self.toggleRadioSix)


		startButton = QPushButton("Start Simulation")
		startButton.clicked.connect(self.startSim)

		stopButton = QPushButton("Stop Simulation")
		stopButton.clicked.connect(self.pauseSim)

		resetButton = QPushButton("Reset Simulation")

		layout = QVBoxLayout()
		layout.addWidget(self.r1coeffedit)
		layout.addWidget(self.r2coeffedit)
		layout.addWidget(self.r3coeffedit)
		layout.addWidget(radioButton1)
		layout.addWidget(radioButton2)
		layout.addWidget(radioButton3)
		layout.addWidget(radioButton4)
		layout.addWidget(radioButton5)
		layout.addWidget(radioButton6)
		layout.addWidget(startButton)
		layout.addWidget(stopButton)
		layout.addWidget(resetButton)
		self.simulationControlBox.setLayout(layout)


	def add_cells(self, num):
		self.foregroundBrush.setColor(self.cellColor)
		self.foregroundBrush.setStyle(Qt.SolidPattern)

		for _ in range(num):
			cpx, cpy = np.random.randint(0, 256, 2)
			
			cell = self.sceneState.addCell(cpx, cpy)
			self.graphicsScene.addItem(cell)
		self.sceneState.updateCellCoords()

	def createGraphicsDisplay(self):
		self.graphicsDisplayBox = QGroupBox('Simulation')
		self.graphicsScene = QGraphicsScene()
		self.graphicsScene.setSceneRect(0, 0, 512, 512)
		self.add_cells(2500)
		self.graphicsScene.setBackgroundBrush(self.backgroundColor)
		self.graphicsView = QGraphicsView(self.graphicsScene)
		self.graphicsView.setSceneRect(0, 0, 512, 512)
		layout = QVBoxLayout()
		layout.addWidget(self.graphicsView)
		self.graphicsDisplayBox.setLayout(layout)
		self.sceneState.graphicsScene = self.graphicsScene

	def cellAnimState(self, x, y):
		a = QPoint(x, y)
		b = QPoint(x + 8, y + 8)
		c = QPoint(x + 16, y)

		tri = QPolygonF()
		tri.append(a)
		tri.append(b)
		tri.append(c)
		
		return tri

	def simulationStep(self):
		self.c += 1
		print("running sim step {0}!\n".format(self.c))
		self.sceneState.update_cell_info(self.graphicsScene)
		self.graphicsScene.advance()

	def runSimulation(self):
		print("Running simulation\n")
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.simulationStep)
		self.timer.start(1000/33)



if __name__ == '__main__':
	app = QApplication([])
	widgets = MenuController()
	widgets.show()
	app.exec_()
