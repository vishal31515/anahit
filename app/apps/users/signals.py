from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from users.models import User
from subscription.models import Subscription, Plan
from allauth.account.signals import email_confirmed
from django.contrib import messages


@receiver(pre_save, sender=User)
def update_username_from_email(sender, instance, **kwargs):
	user_email = instance.email
	username = user_email[:30]
	n = 1
	while User.objects.exclude(pk=instance.pk).filter(username=username).exists():
		n += 1
		username = user_email[:(29 - len(str(n)))] + '-' + str(n)
	instance.username = username

# @receiver(post_save, sender=User)
# def assign_free_plan(sender, instance, created, **kwargs):
# 	if created:
# 		try:
# 			plan_obj = Plan.objects.get(plan_name="Free")
# 		except Plan.DoesNotExists:
# 			print("Plan Does not exist") 
# 		else:
# 			subscription_obj, updated_obj = Subscription.objects.get_or_create(plan=plan_obj, user=instance)
# 			subscription_obj.save()


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    messages.success(request, 'Your email has been successfully verified. ',extra_tags = 'email_confirmed')





