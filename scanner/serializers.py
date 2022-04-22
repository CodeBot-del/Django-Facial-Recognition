from rest_framework.serializers import ModelSerializer
from scanner.models import ScannedImage, OriginalImage




class ScannedImageSerializer(ModelSerializer):
    class Meta:
        model = ScannedImage
        fields = '__all__'
        
        
class OriginalImageSerializer(ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = '__all__'
        
        



