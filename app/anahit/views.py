import json
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic import View
from common.utils import sending_mail
from django.conf import settings
from blog.models import *

def error_404_view(request, exception):
	return render(request,'404.html')


class Homepage(TemplateView):
	template_name = 'home.html'
	def get(self,request):
		single_blog = Post.objects.filter(published=True).first()
		blogs = Post.objects.filter(published=True)[1:3]
		return render(request,self.template_name, locals())

class AboutUs(View):
	template_name = 'about_us.html'
	def get(self,request):
		return render(request,self.template_name)

class ContactUs(View):
	template_name = 'contact_us.html'
	def get(self,request):
		return render(request,self.template_name)
	def post(self,request):
		name = request.POST.get("full_name")
		email = request.POST.get("email_address")
		phone_number = request.POST.get("phone_number")
		message = request.POST.get("message")
		mail_send = sending_mail(
							subject=f"Query from {name}",
							template_name="contactus_alerts",
							template_data={"name":name,
										"email":email,
										"phone_number":phone_number,
										"message":message
										},
							to_email=settings.EMAIL_HOST_USER
						)
		return HttpResponseRedirect('thankyou')



def error_404_view(request, exception):
	return render(request,'404.html')


class ThankYou(View):
	template_name = 'thank_you.html'
	def get(self,request):
		return render(request,self.template_name)

class ChangeTheme(View):

	def post(self,request):
		response = {}
		try:
			light_mode = True if request.POST.get("light_mode") == "true" else False
			if light_mode:
				request.session['light_mode'] = True
				request.session.save()
			else:
				request.session['light_mode']	 = False
				request.session.save()
			response['status'] = True
			response['message'] = "Theme changed successfully"
		except Exception as error:
			response['status'] = False
			response['error'] = str(error)
		return HttpResponse(json.dumps(response),content_type="application/json")

class LinkExpiredView(View):
	def get(self, request):
		return render(request, 'account/link_expired.html')