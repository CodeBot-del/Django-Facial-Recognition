from django.shortcuts import render
import cv2
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
import os
from deepface import DeepFace 


# Create your views here.
def index(request):
    scans = 200
    return render(request, 'index.html', {'scans': scans})

#function to encode all images in the directory
def findEncodings(images):
    encodeList = [] 
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0] 
        encodeList.append(encode)
    return encodeList

def scan(request):
    mode = request.POST['mode']
    message = mode
    
    if mode == "Facial Scan":
        
        image = "/home/egovridc/Desktop/rielle.jpg"
        db_path = '/home/egovridc/Desktop/images'
        model_name = 'Facenet'
        
        #pass a data frame to store results 
        df = DeepFace.find(img_path = image, db_path = db_path, model_name = model_name)
        
        if not df.empty:
            #if dataframe returns similar faces, pass message as Authorized 
            result= "Authorized"
        else:
            result="Unknown"
            
        img = cv2.imread(image)
        imgS = cv2.resize(img,(0,0),None,0.25,0.25) #compress the image to improve performance
        imgS = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) 
        
        facesCurFrame = face_recognition.face_locations(imgS)

        for faceLoc in facesCurFrame:
            if result == "Authorized":
                y1,x1,y2,x2 = faceLoc
                # y1,x1,y2,x2 = y1*4,x1*4,y2*4,x2*4 
                new_image = cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                new_image = cv2.rectangle(new_image, (x1,y2-35),(x2,y2),(0,255,0), cv2.FILLED) #starting point on height reduced by -35 to be a little lower so we can write the name on top of this rectangle
                new_image = cv2.putText(new_image,result, (x2, y2-6), cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                _, frame_buff = cv2.imencode('.jpg', new_image)
                im_bytes = frame_buff.tobytes()
                frame_b64 = base64.b64encode(im_bytes)
                new_img = frame_b64.decode()
                
                return render(request, 'scan.html', {"message":message, "img": new_img})
            else:
                y1,x1,y2,x2 = faceLoc
                new_image = cv2.rectangle(img,(x1,y1),(x2,y2),(0,0,255),2)
                new_image = cv2.rectangle(new_image, (x1,y2-35),(x2,y2),(0,0,255), cv2.FILLED) #starting point on height reduced by -35 to be a little lower so we can write the name on top of this rectangle
                new_image = cv2.putText(new_image,result, (x2, y2-6), cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                _, frame_buff = cv2.imencode('.jpg', new_image)
                im_bytes = frame_buff.tobytes()
                frame_b64 = base64.b64encode(im_bytes)
                new_img = frame_b64.decode()
                
                return render(request, 'scan.html', {"message":message, "img": new_img})
    
    else:
        picha = "/home/egovridc/Desktop/qrcode.png"
        new_image = cv2.imread(picha)
        _, frame_buff = cv2.imencode('.jpg', new_image)
        im_bytes = frame_buff.tobytes()
        frame_b64 = base64.b64encode(im_bytes)
        new_img = frame_b64.decode()
        return render(request, 'scan.html', {"message":message, "img": new_img})
        
        
        
               
    
    # _, frame_buff = cv2.imencode('.jpg', frame) 
    # im_bytes = frame_buff.tobytes()
    # frame_b64 = base64.b64encode(im_bytes)
    # new_img = frame_b64.decode()
    


    