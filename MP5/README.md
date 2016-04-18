Documentation
---------------

# Credits
This program was cowritten by Anna Buchele and Lydia Zuehsow, c. 2016

#Function
This program allows you to control a fake mouse cursor in pygame with a green object and your laptop webcam.

#User instructions
To run this program, you will need OpenCV, imutils, os, sys, argparse, pygame, time, and numpy packages installed.
Make sure your webcam is plugged in/on/etc before running this program.
Also, check to see if there are any other green objects in the webcam's view that are not your intended control mechanism.

	CALIBRATION: Hold the green object steady in the center of the screen to calibrate upon startup of program.
	MOUSE MOVEMENT: Moving the green object will move the cursor in pygame.
	MOUSE SELECTION: Moving the green object a certain distance closer to the webcam will trigger the mouse's "select" mode. The cursor will change shape, and you will be able to interact with 				desktop objects.
	OPENING WINDOWS: Quickly (in less than 20 frames) enter select mode and exit select mode while hovering over a folder. This can be done by moving your object close to the webcam and then regaining 				distance.
	CLOSING WINDOWS: While in select mode, hover over the red circle at the top right hand corner of the window.
	DRAGGING: While in select mode, hover over folders or the tops of windows to select them as well. Once selected, they will snap to your mouse's position until your mouse exits selection mode.

#Change log
Written initially for Olin College's Software Design course, miniproject 4: Interactive Programming. Blank project file forked from class repo. 3/3/16-3/10/16
Edited by Lydia Zuehsow for Olin College's Software Design course, miniproject 5: Feedback and Revision. Mouse selection function added, calibration optimized. 4/16/16
