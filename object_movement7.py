from collections import deque
import cv2
import imutils
import os, sys
import argparse
import pygame
from pygame.locals import *
import time
import numpy as np

class WebCam(object):
	def __init__(self, bufsize = 100, counter = 0):
		"""Run webcam, find green, return center coordinates?"""
		self.camera = cv2.VideoCapture(0)
		#construct argument parse, parse arguments
		self.ap = argparse.ArgumentParser()
		self.ap.add_argument("-v","--video",
			help="path to the(optional) video file")
		self.bufsize = bufsize
		self.ap.add_argument("-b", "--buffer", type=int, default = 100,
			help="max buffer size")
		self.pts = deque(maxlen=bufsize)
		self.counter = counter


	def getcenter(self, greenLower, greenUpper):
		self.args = vars(self.ap.parse_args())

		#initialize tracked points, frame counter, coordinate deltas

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
			((x,y),radius) = cv2.minEnclosingCircle(c)
			Mlist= [M["m10"], M["m00"],M["m01"],M["m00"]]
			if any(Mlist) == 0:
				return None
			else:
				center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
				return [center,radius]

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
		pygame.draw.circle(screen,blueColor,(model.cursor.x,model.cursor.y),20,0)
		pygame.display.update()

class Mouse(object):
	"""Represents the mouse cursor"""
	def __init__(self, mousex=100, mousey=100):
		self.x = mousex
		self.y = mousey
	def initialsetup(self):
		pygame.mouse.set_pos(self.x,self.y)
	def MoveH(self,dY):
		if 0 < (self.x + dX/300) < screenwidth:
			self.x = self.x + (dX/100)
		elif (self.x + dX/300)> screenwidth:
			self.x = screenwidth - 10
		elif (self.x + dX/300) < 0:
			self.x = 10
		pygame.mouse.set_pos(self.x,self.y)
	def MoveV(self,dY):
		if 0 < (self.y + dY/300) < screenheight:
			self.y = self.y + (dX/100)
		elif (self.y + dY/300)> screenheight:
			self.y = screenheight - 10
		elif (self.y + dY/300) < 0:
			self.y = 10
		pygame.mouse.set_pos(self.x,self.y)



class Calibration(object):
	"""Performs calibration of the 'green thing' and represents the calibrated original "green object" """

class DesktopModel(object):
	"""Stores the fake desktop state"""
	def __init__(self):
		self.cursor = Mouse()
		self.desktop = screen.fill(whiteColor)

class Controller(object):
	def __init__(self,model):
		self.model = model
	def process_events(self):
 		"""Process all of the events in the queue"""
 		for event in pygame.event.get():
			print event.type
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == GREENMOVEH:
				# if the event is for horizontal movement,
				# we pop out the first value of the list of 
				# dXs, then run the cursor function for horizontal movement
				dX = dXs.pop(0)
				cursor.MoveH(dX)
			elif event.type == GREENMOVEV:
				# if the event is for vertical movement,
				# we pop out the first value of the list of 
				# dYs, then run the cursor function for vertical movement
				dY = dYs.pop(0)
				cursor.MoveV(dY)
		pygame.event.clear()
		return True


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
	master = Controller(model)




	"""WEBCAM STUFF"""

	#initialize stuff
	webcam = WebCam()
	cursor = Mouse()
	cursor.initialsetup()

	greenLower= (50,65,50)
	greenUpper= (75,255,150)

	counter = 0
	(dX,dY) = (0,0)
	dXs=[]
	dYs=[]

	# Create new event for vertical and horizontal green movements
	GREENMOVEH = pygame.USEREVENT+1
	moveH_event= pygame.event.Event(GREENMOVEH)
	GREENMOVEV = pygame.USEREVENT+2
	moveV_event= pygame.event.Event(GREENMOVEV)

	# makes sure only the events we want are on the event queue
	allowed_events = [GREENMOVEV,GREENMOVEH,QUIT]
	pygame.event.set_allowed(allowed_events)

	buf = 10
	# "buf" is the buffer- the number of frames we go backwards 
	# to compare for movement- so if buf is 10, we compare 
	# the location of the "green" in the current frame 
	# to its location 10 frames earlier. 
	

	"""RUNTIME LOOP"""

	#This is the main loop of the program. 
	running = True
	frame = 0
	eventcount = 0
	while running:
		
		master.process_events()

		#Find the center of any green objects' contours

		gotcenter = webcam.getcenter(greenLower, greenUpper)
		if gotcenter == None:
			continue
		else:
			center = gotcenter[0]
			radius = gotcenter[1]
			cv2.circle(webcam.frame,center,5,(0,0,255), -1)

			if radius > 20:
				#if radius is above a certain size we count it
				webcam.pts.append(center)
				webcam.counter = webcam.counter + 1
				counter = webcam.counter



		for i in range (1,len(webcam.pts),5):
			# ignoring tracked points that are None
			if webcam.pts[i-1] is None or webcam.pts[i] is None:
				continue
			#making sure we have enough points
			if webcam.counter >= buf and webcam.pts[i-buf] is not None:
				#compute difference between x and y coordinates of the point and the point
				#minimum buffer length before it
				dX = webcam.pts[i-buf][0] - webcam.pts[i][0]
				dY = webcam.pts[i-buf][1] - webcam.pts[i][1]
				if np.abs(dX) > 100:
					print dX
					dXs.append(dX)
					pygame.event.post(moveH_event)
				if np.abs(dY) > 100:
					print dY
					pygame.event.post(moveV_event)
					dYs.append(dY)



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
		if key == ord("q"):
			break
if running == False:
		#release camera, close open windows
		webcam.camera.release()
		cv2.destroyAllWindows() 
