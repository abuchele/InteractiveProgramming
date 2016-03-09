from collections import deque
import cv2
import imutils
import os, sys
import argparse
import pygame
from pygame.locals import QUIT, KEYDOWN
import time

class WebCam(object):
	def __init__(self,bufsize=100):
		"""Run webcam, find green, return center coordinates?"""
		self.camera = cv2.VideoCapture(0)
		#construct argument parse, parse arguments
		self.ap = argparse.ArgumentParser()
		self.ap.add_argument("-v","--video",
			help="path to the(optional) video file")
		self.bufsize = bufsize
		self.ap.add_argument("-b", "--buffer", type=int, bufsize,
			help="max buffer size")


	def getcenter(self, greenLower, greenUpper):
		self.args = vars(self.ap.parse_args())

		#initialize tracked points, frame counter, coordinate deltas
		self.pts = deque(maxlen=webcam.args["buffer"])
		self.counter = 0

		#grab current frame
		(self.grabbed, self.frame) = self.camera.read()
		
		#resize frame, blur frame, conert to HSV color space
		self.frame = imutils.resize(self.frame, width=600)
		blurred = cv2.GaussianBlur(self.frame,(11,11),0)
		hsv = cv2.cvtColor(self.frame,cv2.COLOR_BGR2HSV)

		#construct mask for "green", perform dialations and erosions
		#to remove erronous parts of mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask,None,iterations=1)
		mask = cv2.dilate(mask,None,iterations=1)

		#find contours in the mask, initialize current (x,y) center
		self.cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]

		#only continue if at least one contour is found
		if len(self.cnts) > 0:

			#find largest contour in mask, use it to compute 
			#minimum enclosing circel and centroid for that contour

			c = max(self.cnts,key=cv2.contourArea)
			M = cv2.moments(c)
			((self.x,self.y),self.radius) = cv2.minEnclosingCircle(c)
			Mlist= [M["m10"], M["m00"],M["m01"],M["m00"]]
			if any(Mlist) == 0:
				pass
				return False
			else:
				center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))

				return center

class PygameView(object):
	"""Visualizes a fake desktop in a pygame window"""
	def __init__(self,model, screen):
		"""Initialise the view with a specific model"""
		self.model = model
		self.screen = screen
		redColor = pygame.Color(255,0,0)
		greenColor = pygame.Color(0,255,0)
		blueColor = pygame.Color(0,0,255)
		whiteColor = pygame.Color(255,255,255)


	def draw(self):
		"""Draw the game state to the screen"""
		desktop = DesktopModel()
		pygame.draw.circle(screen,blueColor,(model.cursor.x,model.cursor.y),model.cursor.width,0)
		pygame.display.update()

class Mouse(object):
	"""Represents the mouse cursor"""
	def __init__(self, mousex, mousey, width, height):
		self.x = mousex
		self.y = mousey
		self.width = width
		self.height = height

class DesktopModel(object):
	"""Stores the fake desktop state"""
	def __init__(self):
		self.cursor = Mouse(100, 100, 25, 25)
		self.desktop = screen.fill(whiteColor)

class OpenCVController(object):
	def __init__(self,model):
		self.model = model
	def getEvent(self, model, event):
 		"""Look for left and right Pygame Events"""
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == GREENMOVEH:
			if 0 < (mousex + dX/300) < screenwidth:
				model.cursor.x = model.cursor.x - (dX/100)
			elif model.cursor.x > screenwidth:
				model.cursor.x = screenwidth - 10
			elif model.cursor.x < 0:
				model.cursor.x = 10
			pygame.mouse.set_pos(model.cursor.x,model.cursor.y)
		if event.type == GREENMOVEV:
			if 0 < (model.cursor.y + dY/600) < screenheight:
				model.cursor.y = model.cursor.y - (dY/600)
			elif model.cursor.y > screenheight:
				model.cursor.y = screenheight -10
			elif model.cursor.y < 0:
				model.cursor.y = 10
			pygame.mouse.set_pos(model.cursor.x,model.cursor.y)			

if __name__ == '__main__':

	"""Initializing"""

	#Initialize pygame
	pygame.init()

	# Define some colors
	redColor = pygame.Color(255,0,0)
	greenColor = pygame.Color(0,255,0)
	blueColor = pygame.Color(0,0,255)
	whiteColor = pygame.Color(255,255,255)

	#Set pygame fake desktop size
	screenwidth= 1024
	screenheight= 768

	size = (screenwidth, screenheight)
	screen = pygame.display.set_mode(size)

	model = DesktopModel()
	view = PygameView(model, screen)
	controller = OpenCVController(model)

	# Create new event for vertical and horizontal green movements
	GREENMOVEH = pygame.USEREVENT+1
	moveH_event= pygame.event.Event(GREENMOVEH)
	GREENMOVEV = pygame.USEREVENT+2
	moveV_event= pygame.event.Event(GREENMOVEV)

	"""WEBCAM STUFF"""

	greenLower= (29,86,6)
	greenUpper= (64,255,255)

	(dX,dY) = (0,0)

	webcam = WebCam()


	#This is the number of frames before that we will go to calculate dX and dY
	buf = 10

	"""RUNTIME LOOP"""

	running = True
	frame = 0
	while running:
		for event in pygame.event.get():
			controller.getEvent(model, event)

		#Find the center of any green objects' contours
		center = webcam.getcenter(greenLower, greenUpper)

		#If a contour exists...
		if len(webcam.cnts) > 0:
			if webcam.radius > 10:

				# Draws the minimum enclosing circle for the contour
				cv2.circle(webcam.frame,(int(webcam.x),int(webcam.y)),int(webcam.radius),
				(0,255,255),2)
				cv2.circle(webcam.frame,center,10,(255,255,255), -1)

				webcam.pts.appendleft(center)
				webcam.counter = webcam.counter+1
			for i in webcam.pts:
				#ignoring tracked points that are None
				if webcam.pts[i] is None or webcam.pts[i-1] is None:
					continue
				#making sure we have enough points
				if (webcam.counter >= webcam.bufsize) and webcam.pts[i-1] is not None:
					#compute difference between x and y coordinates of the point and the point
					#minimum buffer length before it
					dX = pts[i-buf][0] - pts[i][0]
					dY = pts[i-buf][1] - pts[i][1]



		# Update the frames of the webcam video
		cv2.imshow("Frame",webcam.frame)
		key = cv2.waitKey(1) & 0xFF

		# (cursor.mousex,cursor.mousey) = center

		# Update the fake pygame desktop
		view.draw()

		#Eliminates accidental infinity loops by setting a frame limit on runtime.
		frame += 1
		if frame > 200:
			running = False

		time.sleep(.001)
if running == False:
		#release camera, close open windows
		webcam.camera.release()
		cv2.destroyAllWindows() 
