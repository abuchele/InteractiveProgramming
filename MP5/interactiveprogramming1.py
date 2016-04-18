""" Anna Buchele and Lydia Zuehsow """
""" This program allows you to control a fake mouse cursor in pygame with a green object and your laptop webcam. """

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
		self.counter = counter
		self.calpts = deque(maxlen=bufsize)
		self.calrad = []
		self.calcounter = counter


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
			(center,radius) = cv2.minEnclosingCircle(c)
			Mlist= [M["m10"], M["m00"],M["m01"],M["m00"]]
			if any(Mlist) == 0:
				return None
			else:
				center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
				return [center,radius]


class Calibration(object):
	"""Performs calibration of the 'green thing' and represents the calibrated original "green object" """
	def __init__(self):
		self=self
	def startup(self,greenLower,greenUpper):

		calibrating = True
		count = 0
		calradi = 0
		calx = 0
		caly = 0
		calxs=[]
		calys=[]

		while calibrating:
			califind = webcam.getcenter(greenLower, greenUpper)
			cv2.rectangle(webcam.frame, (0,0), (600,450), (0,0,0), -1)

			A = "Please hold your object very still"
			B =	"in the center of the screen."
			C = "The system is calibrating."
			D = "This will only take a moment."
			cv2.putText(webcam.frame,A,(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,255,255),3)
			cv2.putText(webcam.frame,B,(10,100),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,255,255),3)
			cv2.putText(webcam.frame,C,(10,360),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,255,255),3)
			cv2.putText(webcam.frame,D,(10,400),cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,255,255),3)

			if califind == None:
				pass
			else:
				calicenter = califind[0]
				caliradius = califind[1]

				if caliradius > 20:
				#if radius is above a certain size we count it
					webcam.calpts.append(calicenter)
					webcam.calrad.append(caliradius)
					webcam.calcounter = webcam.calcounter + 1
					calcounter = webcam.calcounter
			buf = 10
			for i in range (1,len(webcam.calpts)):
			# ignoring tracked points that are None
				if webcam.calpts[i-1] is None or webcam.calpts[i] is None:
					pass
			#making sure we have enough points
				if webcam.calcounter >= buf and webcam.calpts[i-buf] is not None:
					#compute difference between x and y coordinates of the point and the point
					#minimum buffer length before it
					count = count + 1
					calx = webcam.calpts[i][0]
					caly = webcam.calpts[i][1]
					calxs.append(calx)
					calys.append(caly)

					cv2.circle(webcam.frame,(calx,caly),5,(0,0,255), -1)

			cv2.imshow("Frame",webcam.frame)
			key = cv2.waitKey(1) & 0xFF

			#Eliminates accidental infinity loops by setting a frame limit on runtime.

			if count > 100:
				calradi = np.mean(webcam.calrad)
				calx = np.mean(calxs)
				caly = np.mean(calys)
				return [calradi, (calx,caly)]
				running = False


class Mouse(object):
	"""Represents the mouse cursor"""
	def __init__(self, mousex, mousey):
		self.x = mousex
		self.y = mousey
		self.selected = False

		self.cursorimage = pygame.image.load('mouse.png').convert_alpha()
		self.cursorimage = pygame.transform.scale(self.cursorimage, (20,30))

		self.selectimage = pygame.image.load('mouseselect.png').convert_alpha()
		self.selectimage = pygame.transform.scale(self.selectimage, (30,40))

	def initialsetup(self):
		pygame.mouse.set_pos(self.x,self.y)
	def Move(self,X,Y):
		self.x = screenwidth - (X * widthfactor)
		self.y = (Y * heightfactor)

class Folder(object):
	"""Represents a folder object stored on the fake desktop"""
	def __init__(self, folderx, foldery, folderwidth, folderheight):
		self.x = folderx + (folderwidth/2)
		self.y = foldery + (folderheight/2)

		self.cornerx = folderx
		self.cornery = foldery

		self.width = folderwidth
		self.height = folderheight

		self.selected = False

		self.folderimage = pygame.image.load('folder.png').convert_alpha()
		self.folderimage = pygame.transform.scale(self.folderimage, (100,75))

		self.text = myfont.render("Cat pics", 1, (0,0,0))

	def Select(self, mousex,mousey):
		self.x = mousex
		self.y = mousey

		self.cornerx = mousex - (self.width/2)
		self.cornery = mousey - (self.height/2)

class Browser(object):
	"""Represents an open browser window"""
	def __init__(self):
		self.width = 300
		self.height = 200

		self.cornerx = 100
		self.cornery = 100

		self.x = self.cornerx + (self.width/2)
		self.y = self.cornery + (self.height/2)

		self.open = False
		self.selected = False

		self.browserimage = pygame.image.load('browser.png').convert_alpha()
		self.browserimage = pygame.transform.scale(self.browserimage, (self.width,self.height))

		self.contentimage = pygame.image.load('cat.jpg').convert()
		self.contentimage = pygame.transform.scale(self.contentimage, (self.width-125,self.height-75))

	def Select(self, mousex,mousey):
		self.x = mousex - (self.width/2)
		self.y = mousey - 25

		self.cornerx = mousex
		self.cornery = mousey

	def Exit(self):
		print 'Exited program'
		self.open = False
		view.update()


class DesktopModel(object):
	"""Stores the fake desktop state"""
	def __init__(self):
		self.desktop = screen.fill(whiteColor)
		self.SelectFrame = 0

		pygame.display.update()
	def clearscreen(self):
		self.desktop = screen.fill(whiteColor)
		pygame.display.update()
	def DragCheck(self,mousex,mousey,mouseselected,folderx,foldery):
		if mouseselected == True:
			# Check to see if mouse is hovering over folder.
			if (mousex + (folder.width/2)) >= folderx and (mousex - (folder.width/2)) <= folderx and (mousey + (folder.height/2)) >= foldery and (mousey - (folder.height/2)) <= foldery:
				folder.Select(mousex,mousey)
				self.SelectFrame += 1

			# Check to see if mouse is hovering over window
			if mousex >= browser.cornerx and mousex <= (browser.cornerx + browser.width - 150) and mousey >= browser.cornery and mousey <= (browser.cornery + browser.height/2):
				browser.Select(mousex,mousey)

			print mousex, mousey, browser.cornerx, browser.cornery

			# Check to see if mouse is selecting exit button
			if mousex <= (browser.cornerx + browser.width + 150) and mousex >= (browser.cornerx + browser.width-100) and mousey >= (browser.cornery+50) and mousey <= (browser.cornery + 150):
				browser.Exit()

	def SelectCheck(self, mouseselected):
		if self.SelectFrame >= 1 and self.SelectFrame <= 20 and mouseselected == False:
			browser.open = True

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

	def update(self):
		"""Draw the game state to the screen"""
		model.clearscreen()

		screen.blit(folder.folderimage,(int(folder.cornerx),int(folder.cornery)))
		screen.blit(folder.text, (folder.cornerx, folder.cornery + folder.height))

		if browser.open == True:
			screen.blit(browser.browserimage,(int(browser.x), int(browser.y)))
			screen.blit(browser.contentimage,(int(browser.x + 50), int(browser.y + 50)))

		if cursor.selected == False:
			screen.blit(cursor.cursorimage,(int(cursor.x),int(cursor.y)))
		else:
			screen.blit(cursor.selectimage,(int(cursor.x),int(cursor.y)))

		pygame.display.update()

class Controller(object):
	def __init__(self,model):
		self.model = model
	def process_events(self):
 		"""Process all of the events in the queue"""
 		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOVE:
				(X,Y) = center
				cursor.Move(X,Y)
			elif event.type == SELECT:
				cursor.selected = True

		pygame.event.clear()




if __name__ == '__main__':

	"""Initializing"""

	#Initialize pygame
	pygame.init()
	myfont = pygame.font.SysFont("monospace", 15)

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
	#initialize variables

	running = True

	cursor = Mouse(100,100)
	cursor.initialsetup()
	cursor.selected = False

	folder = Folder(100, 100, 100, 75)

	browser = Browser()

	frame = 0
	eventcount = 0
	webcam = WebCam()

	webcamwidth = webcam.camera.get(3)
	webcamheight = webcam.camera.get(4)

	widthfactor = (screenwidth / webcamwidth) + 0.1
	heightfactor = (screenheight / webcamheight) + 0.1

	greenLower= (29,86,6)
	greenUpper= (64,255,255)

	X = 0
	Y = 0

	center = 0
	prevcenter = (0,0)
	prevradius = 100

	calibrate = Calibration()
	[calradi,(calx,caly)] = calibrate.startup(greenLower,greenUpper)

	counter = 0
	calcounter = 0

	# Create new event for vertical and horizontal green movements
	MOVE = pygame.USEREVENT+2
	Move_Event = pygame.event.Event(MOVE)
	SELECT = pygame.USEREVENT+3
	Select_Event= pygame.event.Event(SELECT)

	# makes sure only the events we want are on the event queue
	allowed_events = [MOVE,QUIT,SELECT]
	pygame.event.set_allowed(allowed_events)

	buf = 10
	# "buf" is the buffer- the number of frames we go backwards 
	# to compare for movement- so if buf is 10, we compare 
	# the location of the "green" in the current frame 
	# to its location 10 frames earlier. 
	

	"""RUNTIME LOOP"""

	#This is the main loop of the program. 

	while running:

		#Find the center of any green objects' contours

		gotcenter = webcam.getcenter(greenLower, greenUpper)
		if gotcenter == None:
			pass
		else:
			center = gotcenter[0]
			radius = gotcenter[1]
			cv2.circle(webcam.frame,center,5,(0,0,255), -1)

			if radius > 20:
				#if radius is above a certain size we count it
				# webcam.pts.append(center)
				# webcam.rad.append(radius)

				webcam.counter = webcam.counter + 1
				counter = webcam.counter

				(x,y) = center

				if prevcenter is not center:
					if x <= 0 or x >= screenwidth:
						x = 0
						center = (x,y)
					if y <= 0 or y >= screenheight:
						y = 0
						center = (x,y)
					pygame.event.post(Move_Event)
					prevcenter = center

				# Checking to see if user is "clicking" on something
				if radius >= calradi + 15:
					pygame.event.post(Select_Event)
				else:
					cursor.selected = False

		master.process_events()
		model.DragCheck(cursor.x,cursor.y,cursor.selected,folder.x,folder.y)
		model.SelectCheck(cursor.selected)

		# Update the frames of the webcam video
		webcam.frame = cv2.flip(webcam.frame, 1)
		cv2.imshow("Frame",webcam.frame)
		key = cv2.waitKey(1) & 0xFF

		frame = frame + 1
		
		# Update the fake pygame desktop
		view.update()


		time.sleep(.001)
		if key == ord("q"):
			break
		if key == ord("c"):
			model.SelectFrame = 0

		# Failsafe shutoff in 500 frames
		if frame > 500:
			pygame.quit
			sys.exit()
			break

if running == False:
		#release camera, close open windows
		webcam.camera.release()
		cv2.destroyAllWindows() 
