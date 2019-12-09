import numpy as np 
from numpy import random
import math
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QObject, QDateTime, Qt, QTimer, QPoint, QLineF, QRect, QRectF, QPropertyAnimation, QParallelAnimationGroup
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
		self.__velX = 0.0 #random.randint(-10, 10) // 10
		self.__velY =  0.0 #random.randint(-10 , 10) // 10
		self.__motility_force = np.random.randint(-10, 10, 2) * 0.1
		self.__motility_switch = .005
		self.__state = "nonmotile"
		self.div_coeff = 50
		self.radius = 8
		self.__motility_switch_nonmotile = 0.01
		self.__r1_coeff = max(r1, 0.01)
		self.__r2_coeff = max(r2, 0.01)
		self.__r3_coeff = max(r3, 0.01)
		self.__padding = 30
		self.avpos = np.array([0, 0])
		self.avvel = np.array([0, 0])
		self.collisions = list()
		self.num_cells = 0
		self.__cellColor = QColor(209, 220, 237)
		self.__boundingRect = QRectF(self.__x - 5, self.__y - 5, 20, 20)
		self.draw_force_vec = False

	def vel(self):
		return np.array([self.__velX, self.__velY])
	
	def setvel(self, x, y):
		self.__velX = x
		self.__velY = y

	def X(self):
		return self.__x

	def Y(self):
		return self.__y

	def setX(self, x):
		self.__x = x

	def setY(self, y):
		self.__y = y

	def setState(self, state):
		self.__state = state 

	def resetcoeffs(self, r1, r2, r3):
		self.__r1_coeff = r1
		self.__r2_coeff = r2
		self.__r3_coeff = r3

	def percievedCenter(self, center, n):
		# calculate boid's percieved center from the true center
		cent = (center * n).astype(float)
		cent -= np.array([float(self.X()), float(self.Y())])
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
		#print(pc, ", ", self.X(), ", ", self.Y())
		pc[0] -= self.__x
		pc[1] -= self.__y 
		if(abs(np.linalg.norm(pc)) > 0.001):
			return pc * (1/np.linalg.norm(pc)) * self.__r1_coeff
		else:
			return pc * self.__r1_coeff

	def check_collisions(self, x, y):
		if abs(x - self.X()) <= self.__padding and abs(y - self.Y()) <= self.__padding:
			return True
		return False

	def avoid_collisions(self):
		v2 = [0.0, 0.0]
		print(len(self.collisions))
		for cell in self.collisions:
			rect = cell.boundingRect()
			y = rect.top()
			x = rect.left()
			
			xc = self.__x - (x + self.__padding)
			yc = self.__y - (y + self.__padding)
			v2[0] -= xc
			v2[1] -= yc
		
		if abs(np.linalg.norm(v2)) > 0.001:
			return (v2 / np.linalg.norm(v2)) * self.__r2_coeff
		v2[0] *= self.__r2_coeff
		v2[1] *= self.__r2_coeff
		return v2

	def match_velocity(self, vel, n):
		pv = self.percievedVel(vel, n)
		if abs(np.linalg.norm(pv)) > 0.001:
			v3 = (pv / np.linalg.norm(pv)) * self.__r3_coeff
		else:
			v3 = pv * self.__r3_coeff
		return v3

	def new_pos(self, center, vel, n):
		#v1 = self.towards_center(center, n)#self.towards_center(center, n)
		#v2 = self.avoid_collisions()
		v3 = self.match_velocity(vel, n) #self.match_velocity(vel, n)

		v1v2 = self.r1r2()
		
		nv = v1v2 + v3 + np.array([self.__velX, self.__velY]) + self.__motility_force
		
		if(nv[0] != 0 or (nv[1]) != 0):
			nv = nv/np.linalg.norm(nv)
		
		nv *= 0.5
		
		self.__velX = nv[0]
		self.__velY = nv[1]
		self.__x += self.__velX
		self.__y += self.__velY
		if(self.__x < 0 or self.__x > 256):
			self.__velX = -self.__velX
		if(self.__y < 0 or self.__y > 256):
			self.__velY = -self.__velY
		n = np.random.randint(5)
	
	def switch_motile(self):
		self.__state = "motile"
		self.__motility_force = np.random.randint(-10, 10, 2) * 0.1
		if np.dot(self.__motility_force, np.array([self.__velX, self.__velY]) > 0):
			self.__motility_switch = 0.01
		else:
			self.__motility_switch = 0.1

	def switch_nonmotile(self):
		self.__state = "nonmotile"

	def advance(self, step):
		if (step == 0):
			return

		n = np.random.randint(self.div_coeff)
		if n < 2:
			self.radius += 1
		if(self.__state == "nonmotile"):
			n = np.random.randint(1000)
			if(n < 1000 * self.__motility_switch_nonmotile):
				self.switch_motile()
			else:
				self.setPos(self.__x, self.__y)
				return
		elif(self.__state == "motile"):
			n = np.random.randint(1000)
			if(n < 1000 * self.__motility_switch):
				self.switch_nonmotile()
				self.setPos(self.__x, self.__y)
				return
			elif(np.dot(self.__motility_force, np.array([self.__velX, self.__velY]) > 0)):
				self.__motility_switch = 0.01
			else:
				self.__motility_switch = 0.1

		self.new_pos(self.avpos, self.avvel, self.num_cells)
		self.setPos(self.__x, self.__y)

	def boundingRect(self):
		return self.__boundingRect

	def radius_helper(self, x, y):
		return math.sqrt((self.__x - x)**2 + (self.__y - y)**2)

	def r1r2(self):
		v2 = np.array([0.0, 0.0])
		#print("og cell: {0}, {1}", self.X(), self.Y())
		for cell in self.collisions:
			rect = cell.boundingRect()
			y = rect.top()
			x = rect.left()
			#print(x, y)
			xc = self.__x - x  
			yc = self.__y - y
			
			r = np.array([xc, yc])
			if(r[0] != 0 or r[1] != 0):
				r = r/np.linalg.norm(r)
			
			d = self.radius_helper(x, y)
			if (d == 1):
				d = 1.1
			
			v2 -= (self.__r2_coeff * (1/(d - 1)) - self.__r1_coeff) * r 
		#print(v2)
		return v2

	def paint(self, painter, graphitem, widget):

		painter.setBrush(self.__cellColor)
		if (self.__state == "nonmotile" or abs(self.__velX < 0.1) and abs(self.__velY ) < 0.1):
			painter.drawEllipse(self.__x, self.__y, int(self.radius), int(self.radius))
			self.__boundingRect = QRectF(self.__x - 5, self.__y - 5, 20, 20)
			return
		if (abs(self.__velX) < 0.3 and abs(self.__velY) < 0.3):
			if(abs(self.__velX) > abs(self.__velY)):
				painter.drawEllipse(self.__x, self.__y, int(self.radius + 1), int(self.radius))
				self.__boundingRect = QRectF(self.__x - 5, self.__y - 5, 24, 20)
			else:
				painter.drawEllipse(self.__x, self.__y, int(self.radius), int(self.radius + 1))
				self.__boundingRect = QRectF(self.__x - 5, self.__y - 5, 20, 24)
			return
		if (abs(self.__velX) < 0.5 and abs(self.__velY) < 0.5):
			if(abs(self.__velX) > abs(self.__velY)):
				painter.drawEllipse(self.__x, self.__y, int(self.radius + 2), int(self.radius))
				self.__boundingRect = QRectF(self.__x - 5, self.__y - 5, 26, 20)
			else:
				painter.drawEllipse(self.__x, self.__y, int(self.radius), int(self.radius + 2))
				self.__boundingRect = QRectF(self.__x - 5, self.__y - 5, 20, 26)
			return
		p1 = np.array([self.__x, self.__y])
		vel = np.array([self.__velX, self.__velY])
		vel *= 1/np.linalg.norm(vel)
		p2 = p1 - self.radius * np.array(vel[0], vel[1])
		p1_h = np.array([p1[0], p1[1], 1])
		p2_h = np.array([p2[0], p2[1], 1])
		l1 = np.cross(p1_h, p2_h)
		
		l1 = np.array([l1[0], l1[1]]) / l1[2]
		
		l1 = l1/np.linalg.norm(l1)
 
		p3 = p2 - (self.radius // 2 * l1)
		p4 = p2 + (self.radius // 2 * l1)

		try:
			a = QPoint(int(self.__x), int(self.__y))
		except:
			print("TypeError occured: pos is {0}, {1}".format(self.__x, self.__y))
		#print("{0}, {1}, {2}, {3}, {4}".format((self.__x, self.__y), (p3[0], p3[1]), (p4[0], p4[1]), p2, l1))
		b = QPoint(int(p3[0]), int(p3[1]))
		c = QPoint(int(p4[0]), int(p4[1]))

		tri = QPolygonF()
		tri.append(a)
		tri.append(b)
		tri.append(c)
		painter.drawConvexPolygon(tri)

		minx = min(p1[0], min(p3[0], p4[0]))
		miny = min(p1[1], min(p3[1], p4[1]))

		maxx = max(p1[0], max(p3[0], p4[0]))
		maxy = max(p1[1], max(p3[1], p4[1]))

		w = maxx - minx
		h = maxy - miny

		self.__boundingRect = QRectF(minx - 10, miny - 10, w + 20, h + 20)

		if(self.draw_force_vec):
			painter.setPen(QColor("red"))
			painter.drawLine(self.__x, self.__y, self.__x + self.__velX*10, self.__y + self.__velY*10)
			painter.setPen(QColor("blue"))
			painter.drawLine(self.__x, self.__y, self.__x + self.__motility_force[0]*10, self.__y + self.__motility_force[1]*10)
			painter.setPen(self.__cellColor)

	def shape(self):
		path = QPainterPath()

		path.addEllipse(self.__x, self.__y, 20, 20)
		return path





