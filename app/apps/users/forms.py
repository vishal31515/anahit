from urllib import request
from django import forms
from django.contrib.auth.forms import UserCreationForm
from . models import User , UserPreference , InvestmentCountry
from PIL import Image
from django.forms import ModelForm
from allauth.account.forms import SignupForm ,LoginForm
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib import messages


class UserLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control custom-input'
            })


class UserSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
        self.fields['last_name'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
        # self.fields['data_key'] = forms.CharField(widget=forms.HiddenInput(attrs={'value': settings.GOOGLE_RECAPTCHA_SITE_KEY, 'id':'data_key'}))
        self.fields["email"].label = "Email"
        self.fields["email"] = forms.EmailField(required=False, widget=forms.EmailInput(
            attrs={
                'placeholder': 'E-mail Address',
                'pattern':"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
                }))

        self.fields['email'].required = False    
        self.fields["password1"].widget= forms.PasswordInput(
            attrs={
                'pattern': '(?=^.{8,}$)(?=.*\d)(?=.*[!_@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$',
                'title':'The password must contain atleast one uppercase,one lowercase,one numeric,one special character and length greater than or equals to 8 ',
                'placeholder':'Password'
                }
            )
        self.fields['password1'].required = False    
        self.fields["password2"].widget= forms.PasswordInput(
            attrs={
                'pattern': '(?=^.{8,}$)(?=.*\d)(?=.*[!_@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$',
                'title':'The password must contain atleast one uppercase,one lowercase,one numeric,one special character and length greater than or equals to 8 ',
                'placeholder':'Confirm Password',
                } 
            )
        self.fields["password2"].label='Confirm Password'
        self.fields['password2'].required = False    
        

        field_order = ['first_name','last_name' ,'email', 'password']
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control custom-input'
            })

        try:
            user_email = kwargs.get('data').get('email')
            user_exists = User.objects.get(email = user_email)
            if user_exists:
                print('user_already exists')
                return messages.warning('user_already exists')
        except:
            pass
    def save(self, request):
        user = super(UserSignupForm, self).save(request) 
        return user
class UserPreferenceForm(ModelForm):

    country = forms.ModelChoiceField( queryset=InvestmentCountry.objects.all())
    #country = forms.ModelMultipleChoiceField( queryset=InvestmentCountry.objects.all())

    class Meta:
        model = UserPreference
        fields = ('asset_class','risk','term','objective')

    def __init__(self, *args, **kwargs):
        subscription = kwargs.pop('user_subscription', None)
        super(UserPreferenceForm, self).__init__(*args, **kwargs)
        if subscription is not None and subscription.plan.name == "Ultimate" :
            self.fields['country']= forms.ModelMultipleChoiceField( queryset=InvestmentCountry.objects.all())
        self.fields['country'].required = False    
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control custom-input'
            })
            
