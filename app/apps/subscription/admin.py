from django.contrib import admin

from . models import  Plan, Subscription, Features

admin.site.register(Plan)
# admin.site.register(Subscription)
admin.site.register(Features)


@admin.register(Subscription)
class SubscriptionModelAdmin(admin.ModelAdmin):
    list_display = ['user','status','stripe_sub', 'plan']
