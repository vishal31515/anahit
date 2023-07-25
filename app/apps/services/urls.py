from django.urls import path
from . import views

urlpatterns = (
    # urls for Services
    path('', views.Services.as_view(), name='services'),    
    path('finsight/', views.FinsightView.as_view(), name='finsight'),
    path('finsight-grid-search/', views.FinsightGridSearchView.as_view(), name='finsight-grid-search'), 
    path('finsight-list-search/', views.FinsightListSearchView.as_view(), name='finsight-list-search'), 

    path('real-time-alerts/', views.RealTimeAlertsView.as_view(), name='real-time-alerts'),
    path('real-time-alerts-grid-search/', views.RealTimeAlertsSearchGridView.as_view(), name='real-time-alerts-grid-search'),
    path('real-time-alerts-list-search/', views.RealTimeAlertsSearchListView.as_view(), name='real-time-alerts-list-search'),
    path('real-time-alerts/<slug:slug>', views.ViewNotification.as_view(), name='view_alert'),

)