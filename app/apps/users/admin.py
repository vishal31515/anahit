from django.contrib import admin

from . models import  User , InvestmentCountry , UserPreference

# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'stripe_id', 'email']

admin.site.register(InvestmentCountry)
admin.site.register(UserPreference)