from django.shortcuts import render


# Create your views here.
def index(request):
    scans = 200
    return render(request, 'index.html', {'scans': scans})

def qrcode(request):
    return render(request, 'qrcode.html')