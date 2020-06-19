
import cv2
import numpy as np

# For screenshots
from mss import mss # imports class mss from mss module

# screen and coordinates util functions
from myscreentools import coord2mssroi, cropRegion

# Pynput Mouse
from pynput.mouse import Button
from pynput.mouse import Listener as MouseListener

# Pynput Keyboard
from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Listener as KeyboardListener

# Note: keyboard.Listener and mouse.Listener are already
# threading.Thread objects 

# Threading
from threading import Thread

# Terminator
from terminator import searchAndDestroy


# ######### Monitoring the Keyboard ###########################################

def on_press(key):

    global stopThreads

    if key == KeyCode.from_char('q'):
        stopThreads = True
        #print('Stopps Listener already on press')
        #return False


def on_release(key):

    global stopThreads

    if key == KeyCode.from_char('q') or key == Key.esc:
        stopThreads = True

    if stopThreads:

        print('stopping keyboard listener')
        return False

# ########## Getting ROI coordinates ##########################################

def getCoordinates():
    print('\nClick once on the Top-Left and once again on the Bottom-Right of the '
          'Game Screen Rectangle Area')
    coordinates = []

    def onClick(x, y, button, pressed):

        if pressed and button == Button.left:
            coordinates.append((x,y))
            if len(coordinates) >=2:
                print('Done!')
                mlistener.stop()
                # return False       

    with MouseListener(on_click=onClick) as mlistener:
        mlistener.join()

    return coordinates


def pickROI(showROI=False):
    """Pick Screen ROI"""
    
    coords = cropRegion(getCoordinates(), topCrop=0.15, bottomCrop=0.25)
    roi = coord2mssroi(coords)
    sct = mss() # mss object

    # One Screenshot
    img = np.array(sct.grab(roi))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if showROI:
        showImgTime = 2000
        windowName = 'Screen ROI'
        cv2.imshow(windowName, img)
        
        print(f'Showing ROI for {showImgTime/1000} seconds...') 
        cv2.waitKey(showImgTime)
        cv2.destroyWindow(windowName)

    return coords


# ################ MAIN #######################################################

def main():

    roiCoords = pickROI()

    global stopThreads

    while True:

        stopThreads = False # Flag to stop all running threads

        response = input('\nNow please start the game, then return to this terminal \n'
                         'and press enter as soon as the first enemy appears [q to quit anytime]')
        if response == 'q':
            break

        print('\nSit back and hold my beer \n\nSearching and destroying...')
        print('(Press "q" to quit anytime)')

        kListenerThread =  KeyboardListener(on_press=on_press, on_release=on_release)
        kListenerThread.start()

        searchAndDestroyThread = Thread(target=searchAndDestroy, args=(lambda:stopThreads,roiCoords),
                                        kwargs={'timeOut': 180, 'verbose': False})
        searchAndDestroyThread.start()

       
        # Blocking main Thread until searchAndDestroyThread thread finish
        searchAndDestroyThread.join()
        
        # According pynput documentation the keyboard Listener has already the flag daemon = True
        # which means when the main thread ends. The daemon will be also killed
        #kListenerThread.join()

        kListenerThread.stop() # killing in case searchAndDestroyThread is killed from inside (timeout)
        
        response = input('\nPlay another game (same ROI)? [press enter to continue or q to quit]: ')

        if response == 'q':
            break

    # End reached, closing all openCV open windows if any
    cv2.destroyAllWindows()


if  __name__ == '__main__':
    main()

# the imshow function is not thread safe. A thread must acquire a lock before showing the image 
# and release it afer the specified time in the waitKey function has passed.
#
# In python is really easy, define a lock in your code and add in the run method of your thread:

# with image_lock: 
#      cv2.imshow('image',self.image)
#      cv2.waitKey(25)


