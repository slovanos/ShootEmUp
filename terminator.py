# terminator Functions

import cv2
import numpy as np
import random
import time

# Pynput Mouse
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController

# Pynput Keyboard
from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyboardController

# For screen capture
from mss import mss # imports class mss from mss module

# coords conversion tools
from myscreentools import coord2mssroi, img2ScnCoords

# Mouse and Keyboard controllers:
mouse = MouseController()
keyboard = KeyboardController()


def shoot(targetsCoords, bullets, shootPause=0.2, clicks=1):
    """Positionates Mouse on targets and shoots (clicks)"""

    for target in targetsCoords:

        mouse.position = target
        mouse.click(Button.left, clicks)
        bullets -= clicks
        if bullets <= 0:
            return bullets
        time.sleep(shootPause)

    return bullets


def reload():
    # twice because once is sometimes not catched by the game
    keyboard.press(Key.space)
    time.sleep(0.05)
    keyboard.release(Key.space)
    time.sleep(0.05)
    keyboard.press(Key.space)
    time.sleep(0.05)
    keyboard.release(Key.space)


def detectGuns(img, minTh=102, maxTh=102, show=False):
    """Detects guns by color range"""

    filtered = cv2.inRange(img, np.array([minTh, minTh, minTh]), np.array([maxTh, maxTh, maxTh]))

    cnts, hierarchy = cv2.findContours(filtered,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    targets = []

    for c in cnts:

        (center, radius) = cv2.minEnclosingCircle(c)
        targets.append(center)


    if show:
        cv2.drawContours(img, cnts, -1, (255,0,0), 2)

        for target in targets:
            cv2.circle(img, (int(cX), int(cY)), int(radius), (0, 0, 255), -1)

        cv2.imshow("detected", img)
        cv2.waitKey(10)

    return targets



def detectBodies(img):
    """Detects blobs"""

    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    th = 50

    ret,threshImg = cv2.threshold(grayImg,th,255,cv2.THRESH_BINARY)

    # Invert (in opencv-fincontours blob should be white on black background)
    imgInv = cv2.bitwise_not(threshImg)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))
    imgErosion = cv2.erode(imgInv,kernel)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(4,4))# (3,3)
    imgClosing = cv2.morphologyEx(imgErosion, cv2.MORPH_CLOSE, kernel, iterations=2)

    cnts, hierarchy = cv2.findContours(imgClosing,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    targets = []

    for c in cnts:

        M = cv2.moments(c)
               
        # calculate x,y coordinate of center
        if M["m00"] != 0:

           center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

           targets.append(center)
                 

    return targets



def searchAndDestroy(stop, scnRoiCoords, initBullets=11, timeOut=30, loopPause=0.1, verbose=False):
    
    bullets = initBullets

    roi = coord2mssroi(scnRoiCoords)
    sct = mss()

    nCheckForBodies = 8
    nReload = 9 # nCheckForBodies+1
    nReposition = 1

    noTargetsCount = 0
    checkBodiesCount = 0

    # if for some reason the thread controlling the mouse movement gets crazy
    # and it can't be stopped, it will stop after the given timeOut
    start = time.time()
  
    while True:
      
        imgBGRA = np.array(sct.grab(roi))
        img = cv2.cvtColor(imgBGRA, cv2.COLOR_BGRA2BGR)
        
        targets = img2ScnCoords(scnRoiCoords, detectGuns(img))

        if not targets and checkBodiesCount >= nCheckForBodies:
            
            if verbose: print('Searching Bodies:')
            
            targets = img2ScnCoords(scnRoiCoords, detectBodies(img))
            checkBodiesCount = 0
       
        if targets:

            if verbose: print(f'Targets: {len(targets)}')

            bullets = shoot(targets, bullets, shootPause=0.1, clicks=1)
           
            if bullets <= 0:
                reload()
                bullets = initBullets

            noTargetsCount = 0
            checkBodiesCount = 0
       
        else:
            
            noTargetsCount += 1
            checkBodiesCount += 1

            if bullets <= 2 and noTargetsCount >= nReload:
                if verbose: print('idle time reload...')
                reload()
                bullets = initBullets


            if noTargetsCount == nReposition:
                dx,dy = random.choice([(-40,-40),(40,40),(-40,40),(40,-40)])
                mouse.move(dx,dy)


        if time.time()-start >= timeOut:
            print('Time Out Stopping')
            return
   
        if stop():
            print('Stopping searchAndDestroy')
            return

        time.sleep(loopPause)
