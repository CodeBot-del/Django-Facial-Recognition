from django.urls import path
from . import views

app_name = "scanner"

urlpatterns = [
    path('', views.index, name='index'),
    path('scan', views.scan, name='scan'),
    path('stream', views.stream, name='stream'),
    path('qrstream', views.qrstream, name='qrstream'),
    
    
]