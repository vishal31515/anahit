from django.shortcuts import render
from django.views.generic import View, TemplateView
from requests import request
from subscription.models import Plan,Service, Subscription
from django.conf import settings
from subscription.utils import retrieve_subscription_info as get_info


class PriceView(View):
	
    template_name = 'price/price_view.html'
    def get(self,request):
        context = dict()
        current_plan = None
        try:
            if request.user.is_authenticated:
                current_plan = Subscription.objects.filter(user=request.user).last()
        except Subscription.DoesNotExist:
            current_plan = None
        context['current_plan'] = current_plan
        plans = Plan.objects.filter(is_active=True).order_by('price')
        context = {
                'plans':plans,
                "current_plan":current_plan,
                "Free_Plan_PRICE":settings.FREE_PLAN_PRICE
                }
        return render(request,self.template_name, context)
          