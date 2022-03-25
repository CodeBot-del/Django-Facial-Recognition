from django.shortcuts import render
import cv2
import base64
from io import BytesIO
from PIL import Image


# Create your views here.
def index(request):
    scans = 200
    return render(request, 'index.html', {'scans': scans})

def scan(request):
    mode = request.POST['mode']
    message = mode
    
    img = "/home/egovridc/Desktop/cena.jpeg" 
    frame = cv2.imread(img)
    _, frame_buff = cv2.imencode('.jpg', frame) 
    im_bytes = frame_buff.tobytes()
    frame_b64 = base64.b64encode(im_bytes)
    new_img = frame_b64.decode()
    
    
    
    
    
    
    return render(request, 'scan.html', {"message":message, "img": new_img})

#to capture video class