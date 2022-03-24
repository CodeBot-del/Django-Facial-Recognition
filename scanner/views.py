from django.shortcuts import render


# Create your views here.
def index(request):
    scans = 200
    return render(request, 'index.html', {'scans': scans})

def scan(request):
    mode = request.POST['mode']
    message = mode
    return render(request, 'scan.html', {"message":message})