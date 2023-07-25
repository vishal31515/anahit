from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from anahit.storage_backends import MediaStorage


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avtar  = models.ImageField(storage=MediaStorage())
    phone = models.CharField(max_length=20,null=True, blank=True)
    stripe_id = models.CharField(max_length=20, null=True, blank=True)
    metadata =  models.JSONField(null=True, blank=True)
    country_code = models.CharField(max_length=4,null=True,blank=True)
    date_of_birth = models.CharField(max_length = 50,null = True,blank = True)
    gender = models.CharField(max_length = 20,null = True,blank = True)
    # subscribe_blog_alert = models.BooleanField(default=False)
    stripe_card_id = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return f'{self.email}' if self.email else f'{self.username}'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        first_name = self.first_name or "First Name"
        last_name = self.last_name or "Last Name"
        if self.first_name or self.last_name:
            full_name = '%s %s' % (self.first_name, self.last_name)
        else:
            full_name = '%s %s' % (first_name, last_name)
        return full_name.strip()

    def get_user_plan(self, model):

        subscription_obj = model.objects.filter(user_id = self.id).last()
        plans = {}
        if subscription_obj:
            if subscription_obj.status == settings.SUBSCRIPTION_PLAN_STATUS:
                plans[subscription_obj.plan.plan_name] = self.email
            else:
                
                plans[settings.FREE_PLAN_NAME] = self.email    
        else:
            
            plans[settings.FREE_PLAN_NAME] = self.email
        return plans

    def get_plan(self, model):
        subscription_obj = model.objects.filter(user_id = self.id).last()
        plans = ''
        if subscription_obj:
            if subscription_obj.status == settings.SUBSCRIPTION_PLAN_STATUS:
                plans = subscription_obj.plan.plan_name
            else:
                plans = settings.FREE_PLAN_NAME
        else:
            
            plans = settings.FREE_PLAN_NAME
        return plans

class InvestmentCountry(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name



class UserPreference(models.Model):

    class AssetClass(models.TextChoices):
        STOCK = 'STOCK', _('Stocks')
        CRYPTO = 'CRYPTO', _('Crypto')
        COINS = 'COINS', _('COINS')


    class InvestmentRisk(models.TextChoices):
        LR = 'LR', _('Low Risk and Return')
        MR = 'MR', _('Medium Risk and Return')

    class InvestmentTerm(models.TextChoices):
        ST = 'ST', _('Short Term')
        MT = 'MT', _('Medium Term')
        LT = 'LT', _('Long Term')

    class InvestmentObjective(models.TextChoices):
        CAPITAL_GROWTH = 'CAPITAL_GROWTH', _('Capital growth')
        CAPITAL_PRESERVATION = 'CAPITAL_PRESERVATION', _('Capital preservation')
        CAPITAL_GUARANTEED = 'CAPITAL_GUARANTEED', _('Capital guaranteed')

    class Gender(models.TextChoices):
        MALE = 'Male',_('Male')
        FEMALE = 'Female',_('Female')
        OTHER = 'Other',_('Other')


    user  = models.ForeignKey(User,related_name="user_prefences", 
            null=True, on_delete=models.CASCADE)
    country = ArrayField(models.CharField(max_length=20), null=True, blank=True)       
    asset_class = models.CharField(max_length=10,choices=AssetClass.choices)
    risk = models.CharField(max_length=10,choices=InvestmentRisk.choices)
    term = models.CharField(max_length=10,choices=InvestmentTerm.choices)
    objective = models.CharField(max_length=20,choices=InvestmentObjective.choices)

    def __str__(self):
        return "{}-{}-{}-{}-{}".format(self.user.username , self.asset_class , self.risk , self.term , self.objective) 
    
    @property   
    def get_country_display(self):
        countires =[]
        for country in self.country:
            country = InvestmentCountry.objects.get(code=country)
            countires.append(country.name)
        return ",".join(countires)    


    