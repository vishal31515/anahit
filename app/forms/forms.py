from allauth.account.forms import SignupForm
from django import forms
 
 
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = cleaned_data.get("password")
    confirm_password = cleaned_data.get("confirm_password")

    if password != confirm_password:
        raise forms.ValidationError(
            "password and confirm_password does not match"
        )
 
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.password = self.cleaned_data['password']
        user.email = self.cleaned_data['email']
        user.save()
        return user