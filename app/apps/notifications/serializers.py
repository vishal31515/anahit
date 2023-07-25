from rest_framework import serializers
from .models import NotificationsData
from rest_framework import status
from blog.models import Tag

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationsData
        fields = ['channel', 'subject','asset_class', 'message', 'tags', 'thumbnail']
      
