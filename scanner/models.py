from pickletools import read_uint1
from django.db import models

# Create your models here.


class Image(models.Model):
    caption=models.CharField(max_length=100, null=True, blank=True)
    image=models.ImageField(upload_to="img/%y")
    def __str__(self):
        return self.caption




# APIS
class OriginalImage(models.Model):
    image = models.ImageField(upload_to='media/')
    
    class Meta:
        verbose_name_plural = 'original images'
        
    def __str__(self):
        return self.image
    
class ScannedImage(models.Model):
    image = models.ImageField(upload_to='media/')
    
    class Meta:
        verbose_name_plural = 'scanned images'
        
    def __str__(self):
        return self.image
