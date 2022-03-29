from django.shortcuts import render
import cv2
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
import os
from deepface import DeepFace 
from pyzbar.pyzbar import decode  
from . models import Upload



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
    file = request.POST['filename']
    message = mode
            
    if mode == "Facial Scan":
        
        image = "/home/egovridc/Desktop/FaceProject/"+file
        # image = Upload.objects.latest('image')
        
        db_path = '/home/egovridc/Desktop/FaceProject/images'
        model_name = ['Facenet', 'Dlib', 'OpenFace','ArcFace']
        
        #pass a data frame to store results 
        df = DeepFace.find(img_path = image, db_path = db_path)
        
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
                
                return render(request, 'scan.html', {"message":message,"file":file, "img": new_img})
    
    elif mode == "QR & Bar Code":
        
        file = request.POST['filename']
        cap = "/home/egovridc/Desktop/FaceProject/"+file
        qrimage = cv2.imread(cap)
        
        with open('/home/egovridc/Desktop/FaceProject/data.txt') as f:
            Authenticated = f.read().splitlines()
            
        while True:
            #in case of multiple barcodes
            for barcode in decode(qrimage):
                myData = barcode.data.decode('utf-8')
                print(myData)
                
                if myData in Authenticated:
                    myOutput = 'Authorized'
                    myColor = (0,255,0)
                else:
                    myOutput = 'Un-Authorized'
                    myColor = (0,0,255)
                    
                #get the polygon points from the decoder
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1,1,2))
                #draw polygon around qr code
                cv2.polylines(qrimage, [pts], True, myColor, 5)
                pts2 = barcode.rect
                new_image = cv2.putText(qrimage, myOutput, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_COMPLEX, 2.5, myColor, 2)

                _, frame_buff = cv2.imencode('.jpg', new_image)
                im_bytes = frame_buff.tobytes()
                frame_b64 = base64.b64encode(im_bytes)
                new_img = frame_b64.decode()
                
                return render(request, 'scan.html', {"message":message, "img": new_img})
                    
                
                
        
        
    


    