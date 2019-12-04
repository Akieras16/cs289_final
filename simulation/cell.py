import numpy as np 
from numpy import random
import math
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QObject, QDateTime, Qt, QTimer, QPoint, QRect, QRectF, QPropertyAnimation, QParallelAnimationGroup
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView, QGraphicsItem)
from PyQt5.QtGui import QDoubleValidator, QColor, QPen, QPainter, QPainterPath, QBrush, QPolygonF

class CellGraphicsItem(QGraphicsItem):
	def __init__(self, x, y, r1 = 0.05, r2 = 0.01, r3 = 0.0, parent=None):
		super(CellGraphicsItem, self).__init__(parent)
		self.__x = x
		self.__y = y
		self.__velX = 0.0 #random.randint(1, 10) / 10.0
		self.__velY =  0.0 #random.randint(1, 10) / 10.0
		self.__r1_coeff = max(r1, 0.01)
		self.__r2_coeff = max(r2, 0.01)
		self.__r3_coeff = max(r3, 0.01)
		self.__padding = 25
		self.avpos = np.array([0, 0])
		self.avvel = np.array([0, 0])
		self.collisions = list()
		self.num_cells = 0
		self.__cellColor = QColor(209, 220, 237)


	def vel(self):
		return np.array([self.__velX, self.__velY])

	def X(self):
		return self.__x

	def Y(self):
		return self.__y

	def setX(self, x):
		self.__x = x

	def setY(self, y):
		self.__y = y

	def resetcoeffs(self, r1, r2, r3):
		print("coeffs: ", r1, ", ", r2, ", ", r3)
		self.__r1_coeff = r1
		self.__r2_coeff = r2
		self.__r3_coeff = r3

	def percievedCenter(self, center, n):
		# calculate boid's percieved center from the true center
		cent = (center * n).astype(float)
		cent -= [float(self.X()), float(self.Y())]
		return cent / (n - 1)

	def percievedVel(self, vel, n):
		# calculate boid's percieved velocity from true velocity
		v = (vel * n).astype(float)
		v -= (self.vel()).astype(float)
		v = v/(n - 1)
		return v

	def towards_center(self, center, n):
		# generate velocity to move the boid towards the center
		pc = self.percievedCenter(center, n)
		return (pc - np.array([self.X(), self.Y()])) * self.__r1_coeff

	def check_collisions(self, x, y):
		if abs(x - self.X()) <= self.__padding and abs(y - self.Y()) <= self.__padding:
			return True
		return False

	def avoid_collisions(self):
		v2 = np.array([0.0, 0.0])
		for cell in self.collisions:
			rect = cell.boundingRect()
			y = rect.top()
			x = rect.left()
			v2 -= [self.X() - (x + self.__padding), self.Y() - (y + self.__padding)]
		return v2 * self.__r2_coeff

	def match_velocity(self, vel, n):
		pv = self.percievedVel(vel, n)
		v3 = pv * self.__r3_coeff
		return v3

	def new_pos(self, center, vel, n):
		v1 = center * self.__r1_coeff #self.towards_center(center, n)
		v2 = self.avoid_collisions()
		v3 = vel * self.__r2_coeff #self.match_velocity(vel, n)

		nv = v1 + v2 + v3
		self.__velX = self.__velX + nv[0]
		self.__velY = self.__velY + nv[1]
		self.__x, self.__y = np.array([self.X(), self.Y()]) + np.array([self.__velX, self.__velY])
		

	def advance(self, step):
		if (step == 0):
			return
		self.new_pos(self.avpos, self.avvel, self.num_cells)
		self.setPos(self.__x, self.__y)

	def boundingRect(self):
		return QRectF(self.__x - 0.5, self.__y - 0.5, 16 + 0.5, 8 + 0.5)

	def paint(self, painter, graphitem, widget):
		painter.setBrush(self.__cellColor)

		a = QPoint(self.__x, self.__y)
		b = QPoint(self.__x + 8, self.__y + 8)
		c = QPoint(self.__x + 16, self.__y)

		tri = QPolygonF()
		tri.append(a)
		tri.append(b)
		tri.append(c)
		painter.drawConvexPolygon(tri)

	def shape(self):
		path = QPainterPath()

		a = QPoint(self.__x - self.__padding, self.__y - self.__padding)
		b = QPoint(self.__x + self.__padding, self.__y - self.__padding)
		c = QPoint(self.__x + self.__padding, self.__y + self.__padding)
		d = QPoint(self.__x - self.__padding, self.__y - self.__padding)

		tri = QPolygonF()
		tri.append(a)
		tri.append(b)
		tri.append(c)
		tri.append(d)
		path.addPolygon(tri)
		return path





