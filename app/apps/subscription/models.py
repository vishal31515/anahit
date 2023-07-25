from django.db import models
from users.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Features(models.Model):
    name =  models.CharField(max_length=50)

    def __str__(self):
        return '{}'.format(self.name)

class Service(models.Model):
    name =  models.CharField(max_length=250)
    slug = models.SlugField(max_length = 250, null = True, blank = True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('stripe_checkout', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Service, self).save(*args, **kwargs)

PLAN_TYPE=( 
    ("monthly", "monthly"), 
    ("yearly", "yearly"), 
)
class Plan(models.Model):
    plan_name =  models.CharField(max_length=50,null =True,blank =True)
    price = models.PositiveSmallIntegerField(default=0)
    features = models.ManyToManyField(Features, related_name="plan_features", null=True)
    stripe_price_id = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    plan_type=models.CharField(max_length=40,choices=PLAN_TYPE,default="monthly")
    # rules = models.JSONField()
    # metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        if self.plan_name==None:
            return "Plan NAME IS NULL"
        return self.plan_name


'''class Coupon(models.Model):
    coupon_code = models.CharField(max_length = 40)
    max_redemptions = models.PositiveIntegerField()
    valid_till = models.DateField()
    discount_percentage = models.FloatField(default=0.0)
    is_active = models.BooleanField(default = False)

    def is_valid(self):
        current_date = timezone.localtime(timezone.now()).date()
        if self.valid_till <= self.current_date:
            return True
        else:
             return False

    def __str__(self):
        return self.coupon_code'''

class Subscription(models.Model):
    user  = models.ForeignKey(User,related_name="user_subscription", 
            null=True, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan,related_name="plan_subs", 
            null=True, on_delete=models.CASCADE)

    stripe_sub =  models.CharField(max_length=100)        
    status  = models.CharField(max_length=30)
    created_at = models.DateTimeField(blank=True,null=True)
    period_start = models.DateTimeField(blank=True,null=True)
    period_end = models.DateTimeField(blank=True,null=True)
    logs = models.JSONField(null=True, blank=True)
    uses = models.JSONField(null=True, blank=True)
    notification_channels = ArrayField(models.CharField(max_length=20), null=True, blank=True)


    def __str__(self):
        if self.stripe_sub==None or self.stripe_sub=="":
            return self.user.email
        return '{}'.format(self.stripe_sub)