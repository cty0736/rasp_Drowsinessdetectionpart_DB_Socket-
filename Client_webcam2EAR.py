from scipy.spatial import distance as dist
#from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
#import playsound
import argparse
import imutils
import time
import dlib
import cv2
from socket import * 


EYE_AR_THRESH = 0.27
EYE_AR_CONSEC_FRAMES = 8
COUNTER = 0
ALARM_ON = False


#HOST = '127.0.0.1'
HOST = '27.96.130.164'
#HOST = '192.168.0.11'
PORT = 8009
BUFSIZE = 1024
ADDR = (HOST,PORT)

client_socket = socket(AF_INET, SOCK_STREAM)

try:
    print('Try to Connect')
    client_socket.connect(ADDR)
    print('client connection is success..')
    
except Exception as e:
    print('connection error %s:%s'%ADDR)
    

def sending():
    message = 'Alert(DWS)'
    message = message.encode('utf-8')
    client_socket.send(message)    
def send_nor():
    message_nor = 'Normal'
    message_nor = message_nor.encode('utf-8')
    client_socket.send(message_nor)
def recv_nor():
    nor = client_socket.recv(BUFSIZE)
    return nor
    

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])  #p2,p6
    B = dist.euclidean(eye[2], eye[4])  #p3.p5
    C = dist.euclidean(eye[0], eye[3])  #p1,p4

    ear = (A + B) / (2.0 * C)
    return ear

def earcal():
### for already register driver
    global EYE_AR_CONSEC_FRAMES
    global COUNTER 
    global EYE_AR_THRESH ##socket recv
    global ALARM_ON
    frame = cam.read()
    print('Streaming')
    value = client_socket.recv(BUFSIZE)
    print('EAR:',value.decode('utf-8'))
    EYE_AR_THRESH = float(value.decode('utf-8'))
    
    frame = imutils.resize(frame, width = 640)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    
    count = 2
    # loop over the face detections
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd] #
        rightEye = shape[rStart:rEnd] #
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye) #
        rightEyeHull = cv2.convexHull(rightEye) #
        cv2.drawContours(frame, [leftEyeHull], -1, (66, 244, 197), 1) #
        cv2.drawContours(frame, [rightEyeHull], -1, (66, 244, 197), 1) #
                
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            #sending normal
            send_nor()
            count = count - 1
            recv_nor() #n4
            print('1st')
            

            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                print('3rd')
                if not ALARM_ON:
                    ALARM_ON = True
                    #sending alert
                    sending()
                    count = count - 1
                    print('*******Drowsing!!!!!!*******\n')
                    
                cv2.putText(frame, "Drowsing!!", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        else:
            COUNTER = 0
            ALARM_ON = False
            ###sending Normal
            send_nor()
            count = count-1
            recv_nor() #n4
            print('2nd')
            
               
        cv2.putText(frame, "EAR: {:.3f}".format(ear), (150, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    if count == 1:
        send_nor()
    elif count == 2:
        send_nor() #when no rects
        recv_nor() #n4
        send_nor()
        print('See the Front')
        
    
    
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cv2.destroyAllWindows()
        


def new_earcal():
 ### for new driver
    
    sum = 0
    Loop = 0
    while Loop < 30:
    
        frame = cam.read()
        print('Streaming: Regist EAR of Driver:')
        frame = imutils.resize(frame, width = 400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        
        # loop over the face detections
        ear=0      
        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd] #
            rightEye = shape[rStart:rEnd] #
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye) 
            rightEyeHull = cv2.convexHull(rightEye) 
            cv2.drawContours(frame, [leftEyeHull], -1, (66, 244, 197), 1) 
            cv2.drawContours(frame, [rightEyeHull], -1, (66, 244, 197), 1) 
            cv2.putText(frame, "EAR: {:.3f}".format(ear), (150, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if ear < 0.15:
            print('calulate Num: '+ str(int(Loop)))
        else:
            sum += ear
            Loop += 1
            print('calulate Num: '+ str(int(Loop)))
        cv2.imshow("Frame", frame)
            

    EAR_regist = sum/(Loop+1)
    str_EAR_regist = str(EAR_regist)
    print("Calculated_EAR_Regis: ", EAR_regist)
    
    client_socket.send(str_EAR_regist.encode('utf-8'))
    print('Transfer your average EAR')
        # if Loop == 30:
        #     EAR_regist = Sum/Loops
        #     print("Calculated_EAR_Regis: %.3f", % EAR_regist)
        #     client_socket.send(EAR_regist.encode('utf-8'))
####################################################        
        
####Load Argparse
ap = argparse.ArgumentParser()
ap.add_argument('-p', "--shape-predictor", required = True,
    help = "path to facial landmark predictor")
#ap.add_argument('-a', "--alarm", type = str, default = "",
    #help = "path to alarm .wav file")
#ap.add_argument('-w', "--webcam", type = str, default = 0,
   # help = "index of webcam on system")
args = vars(ap.parse_args())


####Load Dlib 
print("[INFO] Loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

####find Eyes
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

while True:
    ####Recv ON/OFF 
    getdata = client_socket.recv(BUFSIZE)
    
    print('Recieved Data1: ', getdata.decode('utf-8'))
    
    if getdata.decode('utf-8') == 'Webcam2 ON':
        ### turn on the webcam streaming       
        send_nor() #n2
        print("[INFO] Starting video stream thread...")
        cam = WebcamVideoStream(src=0).start()
        
        time.sleep(1.0)
               
        while True:         
            # loop over frames from the video stream         
            getregis = client_socket.recv(BUFSIZE) #receive regist on/off
            regis = getregis.decode('utf-8')
            print('Recieved Data2: ', regis)
            if regis != 'OFF':
                ###Calculate New Drivers EAR and Send socket
                new_earcal() #send 1
                recv_nor() #on/off recv
                send_nor() #n2
                

            elif regis == 'OFF':
                send_nor() #n3
                ####detecting drowsiness
                earcal() #recv send recv send per loop
                onoff = client_socket.recv(BUFSIZE) #receive webcam on/off
                print('LAST:', onoff.decode('utf-8'))
                send_nor() #n2
                if onoff.decode('utf-8') == 'Webcam2 OFF':
                    #send_nor() #n1
                    break


                                
            ###
    elif getdata.decode('utf-8') == 'Webcam2 OFF':
        WebcamVideoStream(src=0).stop()
        cv2.destroyAllWindows()
        send_nor()
    ###
print('closing...')
cv2.destroyAllWindows()

