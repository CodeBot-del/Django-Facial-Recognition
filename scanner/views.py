from django.shortcuts import render
import cv2
import base64


# Create your views here.
def index(request):
    scans = 200
    return render(request, 'index.html', {'scans': scans})

def scan(request):
    mode = request.POST['mode']
    message = mode
    
    img = "/home/egovridc/Desktop/Steve/DjangoTutorial/alpha/scanner/cena.jpeg" 
    frame = cv2.imread(img)
    _, frame_buff = cv2.imencode('.jpg', frame) 
    frame_b64 = base64.b64encode(frame_buff)
    
    
    
    
    return render(request, 'scan.html', {"message":message, 'img': frame_b64})

#to capture video class