from django.contrib import admin
from . models import Image, OriginalImage, ScannedImage

# class UploadAdmin(admin.ModelAdmin):

admin.site.register(Image)
admin.site.register(OriginalImage)
admin.site.register(ScannedImage)
