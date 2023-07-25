import datetime
from django.shortcuts import render
from django.views.generic import View
from django.views.generic import RedirectView
from subscription.models import Subscription
from django.db.models import Q
from .models import Dashboard
from notifications.models import NotificationsData
from subscription.utils import retrieve_subscription_info as get_info, check_plan
from django.conf import settings
from django.http import Http404
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponseRedirect


class Services(View):

    template_name = 'services/services_view.html'
    def get(self,request):
        context = {'user':request.user}
        return render(request,self.template_name)

class FinsightView(View):

    def get(self,request):
        context={}
        queryset = Dashboard.objects.filter(is_active=True).order_by("created_at")
        context['service_list'] = queryset
        context["Free_Plan_PRICE"] = settings.FREE_PLAN_PRICE
        try:
            subscription = Subscription.objects.get(user=request.user)
        except Exception as e: 
            context['user_current_plan'] = None
        else:
            user_current_plan = subscription.plan
            subscription_id = subscription.stripe_sub
            context['info'] = get_info(subscription_id)               
            status_code = context['info']['status_code']
            plan_end_date = context['info']['data']['end_date'] 
            status = context['info']['data']['status']
            if status_code == settings.SUBSCRIPTION_PLAN_STATUS_CODE and status == settings.SUBSCRIPTION_PLAN_STATUS and plan_end_date >= datetime.datetime.now():
                context['user_current_plan'] = check_plan(user_current_plan)
        paginator = Paginator(queryset, per_page=2)
        page_num = int(request.GET.get("page", 1))
        if page_num > paginator.num_pages:
            raise Http404
        queryset = paginator.page(page_num)
        if is_ajax(request):
            user_current_plan = check_plan(user_current_plan)
            return render(request, 'subscription/search_insign_grid.html', {'filter_finsights': queryset, 'user_current_plan':user_current_plan})
        context['services'] = queryset
        return render(request, 'subscription/insign.html', context)


class FinsightGridSearchView(RedirectView):
    """
    Finsights Search View
    """
    template = 'subscription/search_insign_grid.html'
    def search(self, search_id, user):
        context={}
        context["Free_Plan_PRICE"] = settings.FREE_PLAN_PRICE
        filter_finsights = Dashboard.objects.filter(is_active=True)
        if search_id:
            filter_finsights = filter_finsights.filter(Q(title__icontains=search_id)|Q(tags__name__icontains=search_id)).distinct()
        context['filter_finsights'] = filter_finsights
        try:
            subscription = Subscription.objects.get(user=user)
        except Exception as e:
            context['user_current_plan'] = None
        else:
            user_current_plan = subscription.plan
            subscription_id = subscription.stripe_sub
            context['info'] = get_info(subscription_id)               
            status_code = context['info']['status_code']
            plan_end_date = context['info']['data']['end_date'] 
            status = context['info']['data']['status']
            if status_code == settings.SUBSCRIPTION_PLAN_STATUS_CODE and status == settings.SUBSCRIPTION_PLAN_STATUS and plan_end_date >= datetime.datetime.now():
                context['user_current_plan'] = check_plan(user_current_plan)
        return context
     
    def get(self, request, *args, **kwargs):
        context={}
        user = request.user
        search_id = self.request.GET.get('search_id')
        context = self.search(search_id, user)
        
        return render(self.request,self.template,context)

class FinsightListSearchView(RedirectView):
    """
    Finsights Search View
    """
    template = 'subscription/search_insign_list.html'
    def search(self, search_id, user):
        context={}
        context["Free_Plan_PRICE"] = settings.FREE_PLAN_PRICE
        filter_finsights = Dashboard.objects.filter(is_active=True)
        if search_id:
            filter_finsights = filter_finsights.filter(Q(title__icontains=search_id)|Q(tags__name__icontains=search_id)).distinct()
        context['filter_finsights'] = filter_finsights
        try:
            subscription = Subscription.objects.get(user=user)
        except Exception as error:
            pass
        else:
            user_current_plan = subscription.plan
            subscription_id = subscription.stripe_sub
            context['info'] = get_info(subscription_id)               
            status_code = context['info']['status_code']
            plan_end_date = context['info']['data']['end_date'] 
            status = context['info']['data']['status']
            if status_code == settings.SUBSCRIPTION_PLAN_STATUS_CODE and status == settings.SUBSCRIPTION_PLAN_STATUS and plan_end_date >= datetime.datetime.now():
                context['user_current_plan'] = check_plan(user_current_plan)
        return context
     
    def get(self, request, *args, **kwargs):
        context={}
        search_id = self.request.GET.get('search_id')
        context = self.search(search_id, request.user)
        
        return render(self.request,self.template,context)

def is_ajax(request):
    """
    This utility function is used, as `request.is_ajax()` is deprecated.

    This implements the previous functionality. Note that you need to
    attach this header manually if using fetch.
    """

    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

class RealTimeAlertsView(View):

    def get(self,request):
        context = {}    
        queryset = NotificationsData.objects.filter(is_active=True).order_by('-created_at')
        context['alerts_list'] = queryset
        paginator = Paginator(queryset, per_page=2)
        page_num = int(request.GET.get("page", 1))
        if page_num > paginator.num_pages:
            raise Http404
        queryset = paginator.page(page_num)
        if  is_ajax(request):
            return render(request, 'subscription/real_time_search_grid.html', {'filter_alerts': queryset})
        context['alerts'] = queryset
        return render(request, "subscription/real_time.html", context) 


class RealTimeAlertsSearchGridView(RedirectView):

    template = 'subscription/real_time_search_grid.html'
    def search(self, search_id):
        context={}
        filter_alerts = NotificationsData.objects.filter(is_active=True)
        if search_id:
            filter_alerts = filter_alerts.filter(Q(channel_name__icontains=search_id)|Q(subject__icontains=search_id)|Q(message__icontains=search_id)|Q(tags__name__icontains=search_id)).distinct()
        context['filter_alerts'] = filter_alerts
        return context

    def get(self, *args, **kwargs):
        context={}
        search_id = self.request.GET.get('search_id')
        context = self.search(search_id)

        return render(self.request,self.template,context)


class RealTimeAlertsSearchListView(RedirectView):

    template = 'subscription/real_time_search_list.html'
    def search(self, search_id):
        context={}
        filter_alerts = NotificationsData.objects.filter(is_active=True)
        if search_id:
            filter_alerts = filter_alerts.filter(Q(channel_name__icontains=search_id)|Q(subject__icontains=search_id)|Q(message__icontains=search_id)|Q(tags__name__icontains=search_id)).distinct()
        context['filter_alerts'] = filter_alerts
        return context

    def get(self, *args, **kwargs):
        context={}
        search_id = self.request.GET.get('search_id')
        context = self.search(search_id)

        return render(self.request,self.template,context)


class ViewNotification(View):
    template="services/view_notification.html"
    def get(self,request, *args, **kwargs):
        try:
            slug = kwargs.get('slug')
            notification = NotificationsData.objects.get(slug=slug)
            previous_post = NotificationsData.objects.filter(id=notification.id-1).first()
            next_post = NotificationsData.objects.filter(id=notification.id+1).first()

        except NotificationsData.DoesNotExist:
            return HttpResponseRedirect(reverse("real-time-alerts"))
        except Exception as error:
            return HttpResponseRedirect(reverse("real-time-alerts"))
        return render(self.request,self.template, locals())
