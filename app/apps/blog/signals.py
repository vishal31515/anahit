from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from django.core.mail import send_mail
from blog.models import Post
from django.conf import settings
import os


# @receiver(post_save, sender=Post)
# def send_email_notification(sender, instance, **kwargs):
#     user_emai_list = [user.email for user in User.objects.filter(subscribe_blog_alert=True)]
#     if user_emai_list:
#         try:
#             send_mail(
#                 settings.SUBSCRIPTION_SUBJECT,
#                 settings.SUBSCRIPTION_MESSAGE,
#                 settings.EMAIL_HOST_USER,
#                 user_emai_list,
#                 fail_silently=False,
#             )
#         except Exception as e:
#             pass