import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anahit.settings')
django.setup()

from users.models import User
from subscription.models import Subscription
from notifications.models import UserNotificationHistory, NotificationRule
from blog.models import Newsletter, Post
from django.conf import settings
import datetime
from django.contrib.sites.models import Site
from django.template.loader import render_to_string 
from django.core.mail import EmailMessage


def run():
    """
        Update notification history data for free plan users
    """
    rule = NotificationRule.objects.filter(plan__price=settings.FREE_PLAN_PRICE, plan__is_active=True).last()
    if rule:
        rule.notification_limit
        users = User.objects.all()
        for user in users:
            user_plan = user.get_user_plan(Subscription)
            if "Free" in user_plan.keys():
                user_email = user_plan['Free']
                UserNotificationHistory.objects.filter(user__email = user_email).update(notifications_left = rule.notification_limit)
            print(f"Notifications data updated for free plan users\n\n")
    else:
        print(f"Plan not found")


def send_newsletter_notification():
    current_date = datetime.datetime.today()
    previous_date = datetime.datetime.today() - datetime.timedelta(days=7)
    newsletter_users = Newsletter.objects.all().values_list('email', flat = True)
    posts = Post.objects.filter(created_at__range=[previous_date, current_date])
    domain = Site.objects.get_current().domain
    try:
        html_template = os.path.join(settings.BASE_DIR,f'templates/email_templates/notifications_alerts.html')
        html_message = render_to_string(html_template, { 'context': posts, 'domain':domain})
        from_email = settings.EMAIL_HOST_USER
        message = EmailMessage('New Anahit Blogs', html_message, from_email, '',  newsletter_users)
        message.content_subtype = 'html'
        message.send()
        return True
    except Exception as msg:
        return False


# if __name__=="__main__":
#     send_newsletter_notification()