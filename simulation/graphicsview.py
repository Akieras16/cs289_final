import numpy as np 
import sys
from cell import CellGraphicsItem as Cell

class SceneState():
	def __init__(self, wound = False, area = 100.0, angles=2, geometry="line"):
		self.angles = angles
		self.area = area
		self.timefactor = 1.0
		self.iswound = wound
		self.geometry = geometry
		self.r1coeff = 0.01
		self.r2coeff = 0.01
		self.r3coeff = 0.01
		self.division_rate = 1000
		self.cells = list()
		self.visible_cells = list()
		self.cell_coords = list()

	def getGeometry(self):
		return self.geometry

	def setGeometry(self, geo):
		self.geometry = geo

	def getAngles(self):
		return self.angles

	def getArea(self):
		return self.area

	def getTimeFactor(self):
		return self.timefactor

	def getIsWound(self):
		return self.iswound

	def setAngles(self, angles):
		self.angles = angles

	def setArea(self, area):
		print(area)
		self.area = area

	def setTimeFactor(self, timefactor):
		self.timefactor = timefactor

	def setWound(self, wound):
		self.iswound = wound

	def updateCoeffs(self):
		for cell in self.cells:
			cell.resetcoeffs(self.r1coeff, self.r2coeff, self.r3coeff)

	def setR1(self, R1):
		#print(R1, "\n")
		self.r1coeff = R1
		self.updateCoeffs()

	def setR2(self, R2):
		self.r2coeff = R2
		self.updateCoeffs()

	def setR3(self, R3):
		self.r3coeff = R3
		self.updateCoeffs()


	def addCell(self, x, y):
		cell = Cell(x, y, self.r1coeff, self.r2coeff, self.r3coeff)
		cell.setPos(x, y)
		self.cells.append(cell)
		self.cell_coords.append([x, y])
		self.visible_cells.append(cell)
		return cell

	def update_cell_info(self, graphicsScene):
		#self.updateCellCoords()
		avpos = self.averagePosition()
		avvel = self.averageVelocity()
		#print("avpos ", avpos, " avvel: ", avvel)
		for cell in self.cells:
			cell.collisions = graphicsScene.collidingItems(cell)
			cell.avpos = avpos
			cell.avvel = avvel
			cell.num_cells = len(self.visible_cells)
			"""
			if(np.random.randint(self.division_rate) == 42):
				nc = self.addCell(cell.X(), cell.Y())
				nc.collisions = graphicsScene.collidingItems(cell)
				nc.avpos = avpos
				nc.avvel = avvel
				nc.num_cells = len(self.visible_cells)
				print("Cell divided!\n")
			"""

	def removeCellGraphics(self, graphicsItem, graphicsScene):
		if not graphicsItem in self.visible_cells:
			return
		else:
			graphicsScene.removeItem(graphicsItem)
			self.visible_cells.remove(graphicsItem)

	def addCellGraphics(self, graphicsItem, graphicsScene):
		if graphicsItem in self.visible_cells:
			return
		else:
			graphicsScene.addItem(graphicsItem)
			self.visible_cells.append(graphicsItem)

	def getCells(self):
		return self.cells

	def updateCellCoords(self):
		self.cell_coords = [[c.X(), c.Y()] for c in self.visible_cells]

	def averagePosition(self):
		x, y = 0, 0
		for c in self.visible_cells:
			x += c.X()
			y += c.Y()

		x /= len(self.cells)
		y /= len(self.cells)

		return np.array([x, y])

	def averageVelocity(self):
		dx, dy = 0, 0
		for c in self.visible_cells:
			vx, vy = c.vel()
			dx += vx
			dy += vy

		dx /= len(self.cells)
		dy /= len(self.cells)
		return np.array([dx, dy])

	def updatePositions(self):
		avpos = self.averagePosition()
		avvel = self.averageVelocity()

		pos_difs = list()
		pos_comps = list()
		
		for cell in self.cells:
			cell.new_pos(self.cells, avpos, avvel, len(self.cells))

	






