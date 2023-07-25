from django.urls import path

from . import views



urlpatterns = (

    # urls for Subscription
    # path('', views.SubscriptionDetails.as_view(), name='subscription_home'),
    # path('config/', views.stripe_config, name='stripe_config'),
    # path('customer_stripe_details/', views.customer_stripe_details, name='customer_stripe_details'),
    path('create-checkout-session/', views.create_checkout_session, name='checkout_session'),
    # path('create-customer/', views.create_customer, name='create_customer'),
    # path('upgrade_subscription/', views.upgrade_subscription, name='upgrade_subscription'),
    # path('billings/', views.BillingView.as_view(), name='billings'),
    path('plan/', views.plans, name='plans'), 
    path('checkout/<int:product_id>', views.stripe_checkout, name='stripe_checkout'),
    path('create-subscription/', views.createSubscription, name='create-subscription'), 
    path('update-subscription/<str:sub_id>/<str:price_id>/', views.update_subscription, name='update-subscription'),   
    path('success/', views.SuccessView.as_view(), name='stripe_success'),
    path('cancelled/', views.CancelledView.as_view(),name='strip_cancelled'), 
    path('subscription_poll/<sub_id>/', views.subscription_poll, name='subscription_poll'),
    path('webhook/', views.stripe_webhook,name='stripe_webhook'),
    path('cancel-subscription/<str:sub_id>/<str:price_id>/', views.cancel_subscription,name='cancel-subscription'),
    path('update-subscription-status/', views.update_subscription_status,name='update-subscription-status'),


    
)
