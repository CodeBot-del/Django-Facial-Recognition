from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators import gzip
import cv2
import base64
import threading
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
import os
from deepface import DeepFace 
from pyzbar.pyzbar import decode  
# from . models import Upload
import os
from .models import Image
from .form import ImageForm

from rest_framework.generics import ListCreateAPIView,  RetrieveUpdateDestroyAPIView
from .serializers import ScannedImageSerializer, OriginalImageSerializer
from .models import OriginalImage, ScannedImage
# Create your views here.
def index(request):
    scans = 200
    form = ImageForm()
    return render(request, 'index.html', {'scans': scans, "form":form})

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
    if request.method == "POST":
        form=ImageForm(data=request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
            file = request.FILES
            file = file['image'].name
            # obj=form.instance
    # if request.method == 'POST' and request.FILES['upload']:
    #     upload = request.FILES['upload']
    #     fss = FileSystemStorage()
    #     file = fss.save(upload.name, upload)
    #     file_url = fss.url(file)    
    #     image = '/home/egovridc/Desktop/Steve/DjangoTutorial/alpha' + file_url
    
    image = '/home/egovridc/Desktop/Steve/DjangoTutorial/alpha/media/img/22/' + file
    
            
    if mode == "Facial Scan":
        
        
        # image = Upload.objects.latest('image')
        # image = '/home/egovridc/Desktop/FaceProject/3.jpg'
        
        db_path = '/home/egovridc/Desktop/FaceProject/images'
        model_name = ['Facenet', 'OpenFace','ArcFace']
        
        #pass a data frame to store results 
        df = DeepFace.find(img_path = image, db_path = db_path, model_name = model_name[2])
        
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
        
        # file = request.POST['filename']
        cap = image
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

@gzip.gzip_page                  
def stream(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace; boundary=frame")
    except:
        pass
    return render(request, 'live.html')

#to capture video and perform recognition class
class VideoCamera(object):
    
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()
    
    def __del__(self):
        self.video.release() 
    
    def get_frame(self):
        path = '/home/egovridc/Desktop/Steve/FaceRecognitionResearch/imagesRecognition' 
        images = []
        classNames = []
        myList = os.listdir(path)
        print(myList)
        
        #import the images from the directory
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
            
        print(classNames)
        
        encodeListKnown = findEncodings(images)  
        print('################------ Encoding Complete ------################') 
        print(encodeListKnown)
        # some very useful functions here 
        while True:
            image = self.frame
            imgS = cv2.resize(image,(0,0),None,0.25,0.25) #compress the image to improve performance
            imgS = cv2.cvtColor(image,cv2.COLOR_BGR2RGB) #convert the image to RGB
            
            facesCurFrame = face_recognition.face_locations(imgS) #find location of all faces in the image
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame) #find encodings of all the faces in the image

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame): #this grabs both the encodings and the locations of the faces in the current frame
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)  #compare the image encodings with the known encodings
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)  #Find how much the faces differ between the image and the known
                # print(faceDis)
                matchIndex = np.argmin(faceDis)  #take the lowest face distance to be the match 
                # if matchIndex < 0.3:    # accept match index lower than 0.5... for the sake of accuracy
                #     matchIndex = matchIndex
                    
                
                #hii code apa chini ni ya kuchora zile boxes za green kwa wwatu verified, na red kwa wasiokua verified
                
                if matches[matchIndex]:
                    
                    
                    name = classNames[matchIndex].upper()  #Get the Name of the image(person) that matched successfully
                    # print(name)
                    y1,x1,y2,x2 = faceLoc
                    # y1,x1,y2,x2 = y1*4,x1*4,y2*4,x2*4 
                    cv2.rectangle(image,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(image, (x1,y2-35),(x2,y2),(0,255,0), cv2.FILLED) #starting point on height reduced by -35 to be a little lower so we can write the name on top of this rectangle
                    cv2.putText(image,name, (x2, y2-6), cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    # convert video stream kwenda jpg then kwenda bytes kwa ajili ya kui display kene browser
                    _, jpeg = cv2.imencode('.jpg', image) #pitisha izi code baada ya kuchora bounding boxes
                    return jpeg.tobytes()
                    
                    
                    
                else:
                    name = "unknown" 
                    y1,x1,y2,x2 = faceLoc
                    # y1,x1,y2,x2 = y1*4,x1*4,y2*4,x2*4 
                    cv2.rectangle(image, (x1,y1), (x2,y2), (0,0,255),2)
                    cv2.rectangle(image, (x1,y2-35), (x2,y2), (0,0,255), cv2.FILLED) #starting point on height reduced by -35 to be a little lower so we can write the name on top of this rectangle
                    cv2.putText(image, name, (x2, y2-6), cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    _, jpeg = cv2.imencode('.jpg', image) #pitisha izi code baada ya kuchora bounding boxes
                    return jpeg.tobytes()
    
    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()
            
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        

          
@gzip.gzip_page                  
def qrstream(request):
    try:
        cam = VideoCamera2()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace; boundary=frame")
    except:
        pass
    return render(request, 'qrlive.html')      
        
class VideoCamera2(object):
    
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.qrgrabbed, self.qrframe) = self.video.read()
        threading.Thread(target=self.update, args=()).start()
    
    def __del__(self):
        self.video.release() 
    
    def get_frame(self):
        imageqr = self.qrframe
        with open('/home/egovridc/Desktop/FaceProject/data.txt') as f:
            Authenticated = f.read().splitlines()
            
        while True:
            #in case of multiple barcodes
            
            for barcode in decode(imageqr):
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
                cv2.polylines(imageqr, [pts], True, myColor, 5)
                pts2 = barcode.rect
                cv2.putText(imageqr, myOutput, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_COMPLEX, 2.5, myColor, 2)
                _, jpeg = cv2.imencode('.jpg', imageqr) #pitisha izi code baada ya kuchora bounding boxes
                return jpeg.tobytes()
            
    def update(self):
        while True:
            (self.qrgrabbed, self.qrframe) = self.video.read()
                
        
    


class ListCreateOriginalImage(ListCreateAPIView):
    queryset = OriginalImage.objects.all()
    serializer_class = OriginalImageSerializer
    
class ListCreateScannedImage(ListCreateAPIView):
    queryset = ScannedImage.objects.all()
    serializer_class = ScannedImageSerializer