import email
from email.contentmanager import raw_data_manager
import os
from notifications.serializers import NotificationSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from notifications.models import NotificationsData
from common.utils import sending_mail,send_notification_on_discord, send_notification_on_telegram
from subscription.models import Subscription, Plan
from blog.models import Tag
from users.models import User
from .models import UserNotificationHistory, NotificationRule
from django.conf import settings
from .choices import NOTIFICATION_CHANNEL

class SendNotification(APIView):
    """
    Send notifications
    """

    def post(self, request, format=None):
        serializer = NotificationSerializer(data=request.data)
        status_code = status.HTTP_200_OK
        response = dict()
        channel = request.data.get('channel')
        asset_name = request.data.get('asset_class')
        subject = request.data.get('subject')
        response_message = request.data.get('message')
        tags = request.data.get('tags')
        thumbnail = request.FILES.get('thumbnail')
        if serializer.is_valid() is False:
            response["message"] = serializer.errors
        else:
            if channel == NOTIFICATION_CHANNEL[0][0]:
                users = User.objects.all()
                for user in users:
                    user_plan = user.get_user_plan(Subscription)
                    for key, val in user_plan.items():
                        rule = NotificationRule.objects.get(plan__plan_name = key)
                        if key == rule.plan.plan_name:
                            users = User.objects.filter(email = val)
                            for user_obj in users:
                                user_history, created = UserNotificationHistory.objects.get_or_create(
                                    user = user_obj,
                                    notification_channel = NOTIFICATION_CHANNEL[0][0],
                                )
                                if created:
                                    user_subscription = Subscription.objects.filter(user = user_obj).last()
                                    if not user_subscription:
                                        user_plan = Plan.objects.filter(plan_name=rule.plan.plan_name).last()
                                    else:
                                        user_plan = user_subscription.plan
                                    user_history.notifications_left = user_plan.plan_rules.last().notification_limit
                                    user_history.save()
                                try:

                                    if user_history.notifications_left > 0:
                                        sent_mail = sending_mail(
                                            subject,
                                            'crypto_alerts', 
                                            response_message, 
                                            val
                                        )
                                        serializer.save()

                                        if sent_mail:   
                                            user_history.notifications_left = int(user_history.notifications_left) - 1
                                            user_history.save()
                                        else:
                                            print("invalid email available")

                                    else:
                                        print(user_obj, "notification count less than 0")
                                except:
                                    sent_mail = sending_mail(
                                        subject,
                                        'crypto_alerts', 
                                        response_message, 
                                        val
                                    )
                                    serializer.save()
                response['message'] = "email sent"
            elif channel == NOTIFICATION_CHANNEL[1][0]:
                get_status, message = send_notification_on_discord(response_message, thumbnail)
                if get_status:
                    status_code = status.HTTP_200_OK
                    response['message'] = message 
                    serializer.save()
                else:
                    status_code 
            elif channel == NOTIFICATION_CHANNEL[2][0]:
                get_status, message = send_notification_on_telegram(response_message, thumbnail)
                if get_status:
                    status_code = status.HTTP_200_OK
                    response['message'] = message
                    serializer.save()
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response['error'] = message
            else:
                response['error'] = "Invalid channel name. Available channels are email, telegram, discord, "
            
            return Response(response, status=status_code)
        return Response(serializer.errors, status=status_code)