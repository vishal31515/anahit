import random
from pyexpat import model
from django.db import models
from blog.models import Tag
from subscription.models import Plan
from django.utils.text import slugify
from anahit.storage_backends import ServiceMediaStorage


class Dashboard(models.Model):
    title = models.CharField(max_length=255)
    link= models.URLField(max_length=250)
    # thumbnail  = models.ImageField(upload_to='service_thumbnails', blank=True, null=True)
    thumbnail  = models.ImageField(storage=ServiceMediaStorage(), blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    plans = models.ForeignKey(Plan,on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def dashboard_tags(self):
        tag_list = []
        tags = self.tags.all()
        for tag in tags:
            tag_list.append(str(tag))
        return tag_list

    @property
    def notification_tags(self):
        tag_list = []
        tags = self.tags.all()
        for tag in tags:
            tag_list.append(str(tag))
        return tag_list

    def __str__(self):
        return self.title