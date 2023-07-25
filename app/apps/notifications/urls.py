from django.urls import path, include,re_path

from . import views

urlpatterns = (
    # urls for Notification
    path('send_notification/', views.SendNotification.as_view(), name='send-notification'),
    
)