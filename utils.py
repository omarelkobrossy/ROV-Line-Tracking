import cv2
import numpy as np
import serial
ser = serial.Serial('COM6', 9600)

def movement(state):
    if state == 1 or state == 5:
        ser.write("a")
    elif state == 2 or state == 4:
        ser.write("k")
    elif state == 3:
        ser.write("z")

def getbasePoints(img, minpercentage=0.1):
    histyValues = np.sum(img, axis=0)
    histxValues = np.sum(img, axis=1)
    maxyValue = np.max(histyValues)
    maxxValue = np.max(histxValues)
    minyValue = minpercentage*maxyValue
    minxValue = minpercentage*maxxValue
    indexyArray = np.where(histyValues>=minyValue)
    indexxArray = np.where(histxValues>=minxValue)
    baseyPoint = int(np.average(indexyArray))
    basexPoint = int(np.average(indexxArray))
    return basexPoint, baseyPoint


def centralizeY(baseyPoint, state): #Stabalize the vertical altitude
    if state == 1 or state == 3 or state == 5:
        if baseyPoint > 167:
            ser.write("k") #letter k translates to downward
        elif baseyPoint < 75:
            ser.write("l") #letter l translates to upward
        else:
            movement(state)

    else: pass

def centralizeX(basexPoint, state): #Stabalize the horizontal altitude
    if state == 2:
        if basexPoint > 730:
            ser.write("a") #letter a translates to right
        elif basexPoint < 710:
            ser.write("z") #letter z translates to left
        else:
            movement(state)
    elif state == 4:
        if basexPoint > 250:
            ser.write("a")
        elif basexPoint < 230:
            ser.write("z")
        else: 
            movement(state)
    else: pass

def rotation_control(state, maskDialated, sens=0.08):
    biggest = 0
    if state == 1 or state == 3 or state == 5:
        #Get a left portion and a right portion of the screen
        crop_l = maskDialated[0:maskDialated.shape[0], 0:100]
        crop_r = maskDialated[0:maskDialated.shape[0], 860:960]
        contours_left, hierarchy = cv2.findContours(crop_l, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours_right, hierarchy = cv2.findContours(crop_r, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #Get the biggest contour just in case the filter isn't that accurate
        for cnt_l in contours_left:
            area_l = cv2.contourArea(cnt_l)
            if area_l > biggest:
                biggest = area_l
        area_l = biggest
        biggest = 0
        for cnt_r in contours_right:
            area_r = cv2.contourArea(cnt_r)
            if area_r > biggest:
                biggest = area_r
        area_r = biggest
        #print(area_l, area_r)
        #Average the areas of both contours
        avg_area = (area_l+area_r)/2
        #Make sure both portions of the frame that i cropped are not empty
        #Play around with the sens and find what's best for the ROV
        if area_l != 0 and area_r != 0:
            if area_l > area_r:
                #print("AREALEFT: ", area_l, "Area Right: ", area_r)
                if (area_l-area_r)/avg_area > sens:
                    ser.write("o") #letter o means anticlockwise
            elif area_r > area_l:
                if (area_r-area_l)/avg_area > sens:
                    ser.write("p") #letter p means clockwise

        #cv2.imshow("croppedleft", crop_l)
        #cv2.imshow("croppedright", crop_r)


def depth_control(state, maskDialated, sens=0.6):
    pass
