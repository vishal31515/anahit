from django.db import models
from blog.models import Tag
from users.models import User
from subscription.models import Plan
from django.utils.text import slugify
from notifications.choices import NOTIFICATION_CHANNEL 
from anahit.storage_backends import ServiceMediaStorage
import random


class NotificationsData(models.Model):
    channel = models.CharField(max_length=60)
    subject = models.CharField(max_length=60,null=True,blank=True)
    asset_class = models.CharField(max_length=60)
    message = models.TextField()
    thumbnail  = models.ImageField(storage=ServiceMediaStorage(), blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    slug = models.CharField(max_length=255,blank=True, null=True)

    def save(self, *args, **kwargs):
        num = random.randint(10,99)
        try:
            obj = NotificationsData.objects.latest('pk')
            self.slug = "%s"%(slugify(self.asset_class + '-'+ str((obj.id+1) + num)))
            super(NotificationsData, self).save()
        except:
            self.slug = "%s"%(slugify(self.asset_class + '-'+ str(1+num)))
            super(NotificationsData, self).save(*args, **kwargs)

    def __str__(self):
        return self.asset_class
        
class NotificationRule(models.Model):
    class Meta:
        unique_together = (('plan', 'notification_channel'),)
        
    plan = models.ForeignKey(Plan,related_name="plan_rules", 
            null=True, on_delete=models.CASCADE)
    notification_channel = models.CharField(max_length=10,choices=NOTIFICATION_CHANNEL)
    notification_limit=models.PositiveIntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.plan.plan_name} - {self.notification_channel} - {self.notification_limit}"

class UserNotificationHistory(models.Model):

    user = models.ForeignKey(User,related_name="notify_user", 
            null=True, on_delete=models.CASCADE)
    notification_channel = models.CharField(max_length=10,choices=NOTIFICATION_CHANNEL)
    notifications_left=models.PositiveIntegerField(null=True,blank=True)

    def __str__(self):
        return f"{self.user.email} - total notification {self.notifications_left}"