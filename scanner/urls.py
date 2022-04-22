from django.urls import path
from .views import *

app_name = "scanner"

urlpatterns = [
    path('', index, name='index'),
    path('scan', scan, name='scan'),
    path('stream', stream, name='stream'),
    path('qrstream', qrstream, name='qrstream'),
    path('original/', ListCreateOriginalImage.as_view(), name='original-list'),
    path('scanned/', ListCreateScannedImage.as_view(), name='scanned-list'),
    
    
]