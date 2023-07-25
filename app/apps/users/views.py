import datetime
from glob import escape
from multiprocessing import context
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes,force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.http import *
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from . forms import UserPreferenceForm, UserSignupForm
from .models import InvestmentCountry , UserPreference
from allauth.account.views import SignupView , LoginView
from django.views.generic import View, DetailView, ListView, UpdateView, CreateView,FormView,TemplateView,DeleteView
from subscription.models import Subscription, Plan
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import re
import stripe
from django.contrib import messages
from subscription.utils import retrieve_subscription_info as get_info
from datetime import date, datetime as dt
from common.utils import invoice_send


stripe.api_key = settings.STRIPE_SECRET_KEY


User = get_user_model()

# def error_404_view(request, exception):
#     return render(request,'404.html')


def account_activation_sent(request,username,email=None): 
    return render(request, 'account_activation_sent.html',{'username':username,'email':email})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('profile_update')
    else:
        return render(request, 'account_activation_invalid.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class MyAccount(LoginRequiredMixin,View):
    template_name = "my-account.html"
    def get(self,request):
        context = dict()
        setup_intent = stripe.SetupIntent.create(
        payment_method_types=["card"],
        usage= "off_session",
        )
        publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        setup_intent_secret=setup_intent.client_secret, 
        user_gender = UserPreference.Gender.choices
        plans = Plan.objects.filter(is_active=True).order_by('price')
        Free_Plan_PRICE = settings.FREE_PLAN_PRICE
        try:
            subscription = Subscription.objects.get(user=request.user)
            user_current_plan = subscription.plan
            subscription_id = subscription.stripe_sub
            context['info'] = get_info(subscription_id)               
            status_code = context['info']['status_code']
            plan_end_date = context['info']['data']['end_date'] 
            status = context['info']['data']['status']
            status_on = settings.SUBSCRIPTION_PLAN_STATUS
            if plan_end_date >= datetime.datetime.now():
                current_plan = user_current_plan
            else:
                current_plan = None
            current_plan = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            current_plan = None
        except Exception as error:
            pass
        return render(request,self.template_name,locals())

    def post(self,request):
        try:
            email = request.user.email
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            bio = request.POST.get('bio')
            raw_password = request.POST.get('password')
            confirm_pass = request.POST.get('confirm_password')
            country_code = request.POST.get('country_code')
            phone_number = request.POST.get('phone')
            picture = request.FILES.get('picture')      
            gender = request.POST.get('gender')
            birthday = request.POST.get('birthday')     
            user = User.objects.get(email = email) 


            
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if bio:
                user.bio = bio
            if raw_password and confirm_pass:
                if raw_password == confirm_pass:
                    raw_password = make_password(raw_password)
                    user.password = raw_password
                    user.save()
                    messages.success(request,"Password successfully updated.",extra_tags = "password_updated")    
            if picture:
                user.avtar = picture
            if country_code:
                user.country_code = country_code
            if phone_number or phone_number == "":
                user.phone = phone_number
            if gender:
                user.gender = gender
            if birthday:
                user.date_of_birth = birthday
            user.save()
            return HttpResponseRedirect(reverse('my_account'))
        except:
            return HttpResponseRedirect(reverse('my_account'))



class UserPreferenceView(LoginRequiredMixin,View):
    def get(self, request):
        try:

            investment_country = InvestmentCountry.objects.all() 
            asset_choices = UserPreference.AssetClass.choices
            investment_risk = UserPreference.InvestmentRisk.choices
            investment_term = UserPreference.InvestmentTerm.choices
            investment_objective = UserPreference.InvestmentObjective.choices
            user_gender = UserPreference.Gender.choices
            user_plan = Subscription.objects.get(user = request.user)
            free_plan = settings.FREE_PLAN_NAME
            
        except Exception as e:
            print("Exception==========", str(e))
        return render(request,'my-preference.html',locals())

   
    def post(self,request):
        user = User.objects.get(email = request.user.email)
        asset_choices = request.POST.get('asset_choices')
        investment_risk = request.POST.get('investment_risk')
        investment_term = request.POST.get('investment_term')
        investment_objective = request.POST.get('investment_objective')
        country = request.POST.getlist('country')
        obj, created = UserPreference.objects.update_or_create(
                user =user,
                defaults={
                        'asset_class': asset_choices,
                        'risk': investment_risk,
                        'term': investment_term,
                        'objective': investment_objective,
                        'country': country
                        }
            )
        if created:
            messages.success(request,"You have successfully set your preferences. ",extra_tags = "preferences_set")           
        else:
            messages.success(request,"You have successfully updated your preferences. ",extra_tags = "updated")
        return HttpResponseRedirect(reverse('user_preference'))



class UserPreferenceCreateView(View):
    def get(self, request):
        user_subscription = None
        try:
           user_subscription = Subscription.objects.get(user=request.user)
        except Exception as e:
            pass   
        user_preference_form = UserPreferenceForm(user_subscription=user_subscription)
        return render(request, 'users/user_preference_create.html',{'user_preference_form':user_preference_form})

    def post(self, request):
        user_preference_form = UserPreferenceForm(request.POST)
        countries = request.POST.getlist('country')
        countires_array = []
        for country in countries:
            try:
                country = InvestmentCountry.objects.get(id=country)
                countires_array.append(country.code)
            except Exception as e:
                pass  
        if user_preference_form.is_valid():
            user_preference = user_preference_form.save(commit=False)
            user_preference.user = request.user
            user_preference.country = countires_array
            user_preference.save()
            return HttpResponseRedirect(reverse('user_preference'))
        else:
            pass


class UserPreferenceEditView(View):
    def get(self, request , pk):

        user_preference = UserPreference.objects.get(id=pk)

        user_subscription = None
        try:
           user_subscription = Subscription.objects.get(user=request.user)
        except Exception as e:
            pass   
        user_preference_form = UserPreferenceForm(instance= user_preference, user_subscription=user_subscription)
        return render(request, 'users/user_preference_create.html',{'user_preference_form':user_preference_form})

    def post(self, request, pk):
        user_preference = UserPreference.objects.get(id=pk)
        user_preference_form = UserPreferenceForm(request.POST,instance= user_preference)
        countries = request.POST.getlist('country')
        countires_array = []
        
        for country in countries:
            try:
                country = InvestmentCountry.objects.get(id=country)
                countires_array.append(country.code)
            except Exception as e:
                pass    
        if user_preference_form.is_valid():
            user_preference = user_preference_form.save(commit=False)
            user_preference.country = countires_array
            user_preference.save()
            return HttpResponseRedirect(reverse('user_preference'))
        else:
            pass

def checkUserNameAndEmail(request):
    type = request.GET["type"] 
    value = request.GET["value"] 
    if type == "username" :
       user = User.objects.filter(username=value) 
       if len(user) == 0 :
           return HttpResponse(status=200)
       else :
           return HttpResponse(status=202)    
    if type == "email" :
       user = User.objects.filter(email=value) 
       if len(user) == 0 :
           return HttpResponse(status=200)
       else :
           return HttpResponse(status=202)


def card_update(request, *args,**kwargs):
    try:
        if request.method == "POST":
            card_number = request.POST.get('card_number')
            exp_month = request.POST.get('month')
            exp_year = request.POST.get('year')
            cvc = request.POST.get('cvc')
            token = stripe.Token.create(
            card={
                "number": card_number,
                "exp_month": int(exp_month),
                "exp_year": int(exp_year),
                "cvc": cvc
            },
            )
            stripe_id = request.user.stripe_id
            customer = stripe.Customer.retrieve(stripe_id)
            card = stripe.Customer.create_source(
                        stripe_id,
                        source=token,
                        )
            card.save()
            customer.default_source = card.id
            customer.save()
            attach_card = stripe.Customer.modify(
            stripe_id,
            invoice_settings={"default_payment_method": card.id},
            )
            attach_card.save()
            messages.success(request, "Card details updated.", extra_tags = "card_updated")
    except stripe.error.CardError as error:
        messages.error(request, "Invalid Card Details.", extra_tags = "card_error")
    except Exception as error:
        messages.error(request, "Something went wrong.Please try again", extra_tags = "card_error")
        
    return HttpResponseRedirect(reverse('my_account'))


class InvoiceHisotry(LoginRequiredMixin, View):
    template_name = "users/invoice_history.html"
    def get(self,request):
        customer = request.user.stripe_id
        data_list = []
        if customer:
            invoice_history = stripe.Invoice.list(
                customer=customer
                )
            search_invoice = request.GET.get('search_invoice', None)
            for data in invoice_history:
                data_dict = {}
                data_dict['number']=data.number
                data_dict['amount_paid']=data.amount_paid/100
                data_dict['plan_name'] = data.account_name
                data_dict['date']=dt.fromtimestamp(data.created).date()
                data_dict['pdf']= data.invoice_pdf
                data_dict['view_invoice'] = data.hosted_invoice_url
                data_dict['id'] = data.id
                data_list.append(data_dict)
        return render(request,self.template_name,locals())


class SendInvoiceMailPDF(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax and request.method == "GET":
            pdf_name = request.GET.get('file_name')
            data = request.GET.get('pdf_data')
            invoice_send(pdf_name, data, request)
            context={'message':'data sent'}
        return JsonResponse(context)

class MagicLinkLogin(View):
    template_name = 'account/magic_link_login.html'
    def get(self, request):
        return render(request, self.template_name)


class CheckEmailExists(View):
    def get(self, request):
        email = request.GET.get('email')
        email_email = User.objects.filter(email=email).last()
        if email_email:
            context={"data":"email already exists."}
        return JsonResponse(context)