from django.contrib import admin
from .models import NotificationsData, NotificationRule, UserNotificationHistory
# Register your models here.

@admin.register(NotificationsData)
class NotificationDataAdmin(admin.ModelAdmin):
    list_display = ['message', 'channel']



admin.site.register(NotificationRule)
admin.site.register(UserNotificationHistory)
