# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 16:15:05 2013

@author: Ashutosh Raj
"""

import cv2
import datetime
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

fromaddr = "*****************"
toaddr = "*******************"
 
SENSITIVITY_VALUE = 60
BLUR_SIZE = 10
frame_count = 0

def inToString(number):
    x = str(raw_input(number))
    return x
 
def getDateTime():
    now = datetime.datetime.now()
    year = str('{:04d}'.format(now.year))
    month = str('{:02d}'.format(now.month))
    day = str('{:02d}'.format(now.day))
    hrs = str('{:02d}'.format(now.hour))
    minute = str('{:02d}'.format(now.minute))
    sec = str('{:02d}'.format(now.second))
    timestamp = hrs+':'+ minute +':'+ sec
    dateTime = year + "-" + month + "-" + day + "  " + timestamp
    return dateTime


def getDateTimeForFile():
    now = datetime.datetime.now()
    year = str('{:04d}'.format(now.year))
    month = str('{:02d}'.format(now.month))
    day = str('{:02d}'.format(now.day))
    hrs = str('{:02d}'.format(now.hour))
    minute = str('{:02d}'.format(now.minute))
    sec = str('{:02d}'.format(now.second))
    dateTime = year + "_" + month + "_" + day + "_" + hrs +'h'+minute+'m'+sec+'s'
    return dateTime


 
def detectMotion(thresholdImage,cameraFeed):
    global frame_count
    motionDetected = False
    temp = thresholdImage.copy()
    contours,hierarchy = cv2.findContours(temp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if(len(contours)>0):
        motionDetected = True
        frame_count +=1
    else: motionDetected = False
    return motionDetected

def email_sending():
    
    msg = MIMEMultipart()
 
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Intruder Detected"
 
    body = "Video of 15 seconds after the intruder enters"
 
    msg.attach(MIMEText(body, 'plain'))
 
    filename = y
    attachment = open(x, "rb")
 
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
 
    msg.attach(part)
 
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    '''
    Password of the email mentioned.
    '''
    server.login(fromaddr, "*************") 
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print "Email Sent"
    
def main():
    global x,y
    recording = False
    startNewRecording = False
    inc = 0
    firstRun = True
    motionDetected = False
    pause = False
    debugMode = False
    trackingEnabled = True
    capture = cv2.VideoCapture(0)
    fourcc = cv2.cv.CV_FOURCC('D', 'I', 'V', '3')
    dWidth = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    dHeight = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    if (capture.isOpened()==False):
        print "ERROR ACQUIRING VIDEO FEED\n"
        raw_input("Press Enter to continue...")
        return -1
 
    while(1):
        _, frame1 = capture.read()
        grayImage1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        _,frame2 = capture.read()
        grayImage2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        differenceImage = cv2.absdiff(grayImage1,grayImage2)
        _,thresholdImage = cv2.threshold(differenceImage,SENSITIVITY_VALUE,255,cv2.THRESH_BINARY)
        
        if(debugMode == True):
            cv2.imshow("Difference Image",differenceImage)
            cv2.imshow("Threshold Image",thresholdImage)
        thresholdImage = cv2.blur(thresholdImage,(BLUR_SIZE,BLUR_SIZE))
        _,thresholdImage = cv2.threshold(thresholdImage,SENSITIVITY_VALUE,255,cv2.THRESH_BINARY)
        
        if(debugMode == True):
            cv2.imshow("Final Threshold Image",thresholdImage)
            
        if(trackingEnabled):
            motionDetected = detectMotion(thresholdImage,frame1)
            
        else:
            motionDetected = False
        dateTime = getDateTime()
        cv2.rectangle(frame1,(0, 455),(190, 470),(255, 255, 255), -1)
        cv2.putText(frame1, dateTime,(0, 467), 1, 1,(255, 0, 0), 1)
        if (recording):
            if(firstRun == True or startNewRecording == True):
                videoFileName = getDateTimeForFile()
                videoFileName = "D:/" + str(videoFileName) + ".avi"
                print "File has been opened for writing: " + videoFileName
                print "Frame Size = " + str(dWidth) + "x" + str(dHeight)
                oVideoWriter = cv2.VideoWriter(videoFileName,fourcc, 20, (dWidth,dHeight),True)
                if(oVideoWriter.isOpened()== False):
                    print "ERROR: Failed to initialize video writing"
                    raw_input("Press Enter to continue...")
                    return -1
                firstRun = False
                startNewRecording = False
            oVideoWriter.write(frame1)
            cv2.putText(frame1,"REC",(0,60),2,2,(0,0,255),2)
        if(motionDetected):
            cv2.putText(frame1,"KIET SECURITY",(0,420),2,2,(0,255,0))
            cv2.putText(frame1, "INTRUDER DETECTION ",(200,50), 2, 2,(255,50, 100))
            recording = True
        else:
            recording = False
        cv2.imshow("Frame1",frame1)
        k = cv2.waitKey(30)
        
        if k == 27:
            cv2.destroyAllWindows()
            print x
            print frame_count
            return 0

        
        if k == 116:
            trackingEnabled = not trackingEnabled
            if trackingEnabled == False:
                print "Tracking Disabled"
            else:
                print "Tracking Enabled"

            
        if k == 100:
            debugMode = not debugMode
            if debugMode == False:
                cv2.destroyWindow("Difference Image")
                cv2.destroyWindow("Threshold Image")
                cv2.destroyWindow("Final Threshold Image")
                print "Debug Mode Disabled"
            else:
                print "Debug Mode Enabled"

                
        if k == 112:
            pause = not pause
            if pause == False:
                print "Code paused, press 'p' again to resume"
            while (pause==True):
                if k == 112:
                    pause = False
                    print "Code Resumed"
                    break

                
        if k == 114:
            recording = not recording
            if(recording == False):
                print "Recording Stopped"
            else:
                print "Recording Started"

        if frame_count == 126:
            x = videoFileName
            y = x[3:27]
            email_sending()
            startNewRecording = True
        if k == 110:
            startNewRecording = True
            recording = True
            print "New Recording Started"
            inc +=1
    
        
        
  
            
if __name__ == '__main__':
    main()
