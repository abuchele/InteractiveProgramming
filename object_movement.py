#importing packages
from collections import deque
import numpy as np 
import argparse
import imutils
import cv2

#construct argument parse, parse arguments
ap= argparse.ArgumentParser()
ap.add_argument("-v","--video",
	help="path to the(optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size")
args = vars(ap.parse_args())

#define the lower and upper boundaries of what is considered "green"
greenLower= (29,86,6)
greenUpper= (64,255,255)

#initialize tracked points, frame counter, coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX,dY) = (0,0)
direction = ""

camera = cv2.VideoCapture(0)

while True:
	#grab current frame
	(grabbed,frame)= camera.read()

	#resize frame, blur frame, conert to HSV color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame,(11,11),0)
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

	#construct mask for "green", perform dialations and erosions
	#to remove erronous parts of mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask,None,iterations=2)
	mask = cv2.dilate(mask,None,iterations=2)

	#find contours in the mask, initialize current (x,y) center
	cnts = cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	#only proceed if at least one contour was found
	if len(cnts) > 0:
		#find largest contour in mask, use it to compute 
		#minimum enclosing circel and centroid
		c = max(cnts,key=cv2.contourArea)
		((x,y),radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
		#only proceed if radius meets minimum size
		if radius > 10:
			#draw circle and centroid on frame,
			#update list of tracked points
			cv2.circle(frame,(int(x),int(y)),int(radius),
				(0,255,255),2)
			cv2.circle(frame,center,5,(0,0,255), -1)
			pts.appendleft(center)
	for i in np.arange(1,len(pts)):
		#if either of the tracked points are None, ignore them
		if pts[i - 1] is None or pts[i] is None:
			continue

		#check to see if enough points have been accumulated in the buffer
		if counter >= 10 and i ==1 and pts[-10] is not None:

			# compute the difference between the x and y coordinates
			#re-initialize the direction text variables
			dX = pts[-10][0] - pts[i][0]
			dY = pts[-10][1] - pts[i][1]
			(dirX,dirY) = ("","")

			#ensure there is significant movement in the x-direction
			if np.abs(dX) > 20:
				dirX = "East" if np.sign(dX) == 1 else "West"

			#ensure there is significant movement in the y-direction
			if np.abs(dY) > 20:
				dirY = "North" if np.sign(dY) == 1 else "South"

			# handle when both directions are non-empty
			if dirX != "" and dirY != "":
				direction = "{}-{}".format(dirY,dirX)

			#otherwise, only one direction is non-empty
			else:
				direction = dirX if dirX != "" else dirY

		#otherwise, compute the thickness of the line
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"]/float(i +1))*2.5)
		cv2.line(frame,pts[i - 1], pts[i], (0,0,255), thickness)

	#show the movement deltas and direction of movement on frame
	cv2.putText(frame,direction,(10,30),cv2.FONT_HERSHEY_SIMPLEX,
		0.65,(0,0,255),3)
	cv2.putText(frame,"dx: {}, dy: {}".format(dX,dY),
		(10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35,(0,0,255),1)

	cv2.imshow("Frame",frame)
	key = cv2.waitKey(1) & 0xFF


	#if 'q' is pressed stop the loop
	if key == ord("q"):
		break

#release camera, close open windows

camera.release()
cv2.destroyAllWindows()


"""modelview control (inside pygame already)> have object oriented implementation of project (MUST have object-oriented design)


take a look at how to control a mouse inside a python program, may be big problem
next step: interact with pygame object! hook into modelview control ?? 
DO NOT DO TWO WHILE TRUE LOOPS- death upon all 
instead try to hook the two loops together so they run under one loop."""