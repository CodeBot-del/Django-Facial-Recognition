from pickletools import read_uint1
from django.db import models

# Create your models here.
class Upload(models.Model):
    image = models.ImageField(upload_to='media/')
    
   
    